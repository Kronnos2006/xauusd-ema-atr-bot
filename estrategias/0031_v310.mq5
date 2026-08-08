//+------------------------------------------------------------------+
//| 0031.mq5  v3.00                                                  |
//| Judas | Venom | Bernd | LonClose | SilverBullet | CRT           |
//|                                                                  |
//| v3.00 fixes vs v2.10:                                           |
//|  - TimeGMT() en lugar de hora del servidor                      |
//|  - Magic Number propio (filtra CountOpenTrades)                 |
//|  - DailyLossHit usa EQUITY, no balance                          |
//|  - CheckStopsLevel antes de enviar orden                        |
//|  - Filtro de spread configurable                                |
//|  - CRT integrado (H4 por defecto): sweep + confirm + plan       |
//+------------------------------------------------------------------+
#property copyright "Invenio 2026"
#property version   "3.10"
#property strict

#include <Trade\Trade.mqh>
CTrade trade;

//--- Inputs generales
input ulong  InpMagic        = 31000;
input double InpRiskUSD      = 1.0;
input int    InpMaxTrades    = 3;
input double InpMaxLossDay   = 15.0;
input double InpRR_Ratio     = 2.0;
input double InpMaxSpreadPts = 30.0;   // spread máximo en puntos (_Point)
input int    InpServerUTCOffset = 0;     // hora servidor - UTC; usar valor fijo en backtest
input double InpMaxOpenRiskUSD = 3.0;    // riesgo total máximo abierto de este EA
input int    InpEMA_Fast     = 20;
input int    InpEMA_Slow     = 200;

//--- Inputs CRT
input ENUM_TIMEFRAMES InpCRT_HTF      = PERIOD_H4;  // Timeframe de referencia
input double          InpCRT_RR_Min   = 1.5;        // R:R mínimo para confirmar
input double          InpCRT_ATRBuf   = 0.3;        // buffer SL = wick ± X*ATR(M5)
input double          InpCRT_RangeMin = 0.5;        // rango mínimo en múltiplos de ATR(HTF)
input bool            InpCRT_ReArm    = true;       // re-armar si barrido más profundo
input int             InpCRT_MaxSignalsPerRange = 2; // máximo de señales por rango HTF
input int             InpCRT_MaxConfirmBars = 3;     // M5 máximas para confirmar sweep

//--- Handles de indicadores
int g_h_ema20   = INVALID_HANDLE;
int g_h_ema200  = INVALID_HANDLE;
int g_h_atr14   = INVALID_HANDLE;   // ATR14 en M5
int g_h_atr_htf = INVALID_HANDLE;   // ATR14 en HTF para CRT

//--- Control de barra
datetime g_last_bar = 0;

//--- Sesión Asia  00:00-08:00 UTC
double   g_asia_high  = 0, g_asia_low  = 0;
bool     g_asia_ready = false;
datetime g_asia_start = 0;

//--- Sesión Londres  08:00-13:30 UTC
double   g_lon_high   = 0, g_lon_low   = 0;
bool     g_lon_ready  = false;
datetime g_lon_start  = 0;

//--- NY Early  13:30-15:00 UTC
double   g_ny_high    = 0, g_ny_low    = 0;
bool     g_ny_ready   = false;

//--- Flags señal — máximo 1 por estrategia por día
bool g_sig_judas    = false;
bool g_sig_venom    = false;
bool g_sig_bernd    = false;
bool g_sig_lonclose = false;
bool g_sig_silver   = false;
bool g_sig_crt      = false;

//--- Estado CRT
struct CRTState
{
   double   htf_high;
   double   htf_low;
   datetime htf_bar_time;   // tiempo de la vela HTF usada como rango
   bool     swept_high;
   bool     swept_low;
   double   sweep_wick;     // extremo de la mecha del barrido
   bool     confirmed;
   bool     bull;           // true=barrió low → entrega hacia high (LONG)
   bool     plan_active;
   datetime plan_start;
   double   entry;
   double   sl;
   double   tp;
   int      sweep_bar_index;
   int      signals_emitted;
};
CRTState g_crt;

//--- Riesgo diario
double g_equity_start_day = 0;
int    g_utc_day_key = -1;

//--- Auxiliares
int g_obj_count = 0;
int g_file      = INVALID_HANDLE;

datetime ServerTimeToUTC(datetime server_time)
{
   return server_time - (InpServerUTCOffset * 3600);
}

//+------------------------------------------------------------------+
int OnInit()
{
   if(_Period != PERIOD_M5) { Alert("Usar en M5"); return INIT_FAILED; }

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(10);

   g_h_ema20   = iMA(_Symbol, PERIOD_M5, InpEMA_Fast, 0, MODE_EMA, PRICE_CLOSE);
   g_h_ema200  = iMA(_Symbol, PERIOD_M5, InpEMA_Slow,  0, MODE_EMA, PRICE_CLOSE);
   g_h_atr14   = iATR(_Symbol, PERIOD_M5, 14);
   g_h_atr_htf = iATR(_Symbol, InpCRT_HTF, 14);

   if(g_h_ema20   == INVALID_HANDLE || g_h_ema200  == INVALID_HANDLE ||
      g_h_atr14   == INVALID_HANDLE || g_h_atr_htf == INVALID_HANDLE)
   { Print("ERROR: handle inválido"); return INIT_FAILED; }

   ChartIndicatorAdd(0, 0, g_h_ema20);
   ChartIndicatorAdd(0, 0, g_h_ema200);

   g_equity_start_day = AccountInfoDouble(ACCOUNT_EQUITY);
   ZeroMemory(g_crt);

   g_file = FileOpen("0031v300.csv",
      FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ',');
   if(g_file != INVALID_HANDLE)
   {
      FileSeek(g_file, 0, SEEK_END);
      if(FileTell(g_file) == 0)
         FileWrite(g_file, "fecha","hora_utc","estrategia","dir",
            "entrada","sl","tp","lot","spread_pts","atr_m5");
   }

   CreateCornerLabel();
   Print("0031 v3.10 OK | Magic:", InpMagic, " | Símbolo:", _Symbol, " | UTC offset:", InpServerUTCOffset);
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_file != INVALID_HANDLE) { FileClose(g_file); g_file = INVALID_HANDLE; }
   IndicatorRelease(g_h_ema20);
   IndicatorRelease(g_h_ema200);
   IndicatorRelease(g_h_atr14);
   IndicatorRelease(g_h_atr_htf);
   ObjectsDeleteAll(0, "MS_");
}

//+------------------------------------------------------------------+
void OnTick()
{
   datetime bar0 = iTime(_Symbol, PERIOD_M5, 0);
   if(bar0 == g_last_bar) return;
   g_last_bar = bar0;

   // --- UTC de la vela histórica, no UTC de "ahora" ---
   // hora_UTC = hora_servidor - InpServerUTCOffset.
   datetime bar_utc = ServerTimeToUTC(bar0);
   MqlDateTime t;
   TimeToStruct(bar_utc, t);
   int cm = t.hour * 60 + t.min;
   int day_key = t.year * 10000 + t.mon * 100 + t.day;

   // Reset exactamente una vez por día UTC.
   if(day_key != g_utc_day_key)
   {
      g_utc_day_key = day_key;
      DailyReset();
   }

   // Precios (barra cerrada = índice 1)
   double c1 = iClose(_Symbol, PERIOD_M5, 1);
   double c2 = iClose(_Symbol, PERIOD_M5, 2);
   double h1 = iHigh(_Symbol,  PERIOD_M5, 1);
   double l1 = iLow(_Symbol,   PERIOD_M5, 1);
   // Barra actual (para acumular rangos de sesión)
   double h0 = iHigh(_Symbol,  PERIOD_M5, 0);
   double l0 = iLow(_Symbol,   PERIOD_M5, 0);
   double pip = _Point * 10;

   // ATR M5
   double atr_buf[1];
   if(CopyBuffer(g_h_atr14, 0, 1, 1, atr_buf) < 1) return;
   double atr = atr_buf[0];

   // EMAs
   double e20[1], e200[1];
   if(CopyBuffer(g_h_ema20,  0, 1, 1, e20)  < 1) return;
   if(CopyBuffer(g_h_ema200, 0, 1, 1, e200) < 1) return;
   UpdateTrendLabel(c1, e200[0]);

   // =================== SESIONES ===================

   // Asia 00:00-08:00 UTC
   if(cm >= 0 && cm < 480)
   {
      if(g_asia_start == 0) g_asia_start = bar0;
      if(h0 > g_asia_high || g_asia_high == 0) g_asia_high = h0;
      if(l0 < g_asia_low  || g_asia_low  == 0) g_asia_low  = l0;
   }
   if(t.hour == 8 && t.min == 0 && !g_asia_ready && g_asia_high > 0)
   {
      g_asia_ready = true;
      DrawRect("MS_RECT_ASIA", g_asia_start, bar0, g_asia_high, g_asia_low, C'30,30,60', "Asia");
      DrawHL("MS_ASIA_H", g_asia_high, clrOrange, "Asia H");
      DrawHL("MS_ASIA_L", g_asia_low,  clrOrange, "Asia L");
   }

   // Londres 08:00-13:30 UTC
   if(cm >= 480 && cm < 810)
   {
      if(g_lon_start == 0) g_lon_start = bar0;
      if(h0 > g_lon_high || g_lon_high == 0) g_lon_high = h0;
      if(l0 < g_lon_low  || g_lon_low  == 0) g_lon_low  = l0;
   }
   if(t.hour == 13 && t.min == 30 && !g_lon_ready && g_lon_high > 0)
   {
      g_lon_ready = true;
      DrawRect("MS_RECT_LON", g_lon_start, bar0, g_lon_high, g_lon_low, C'40,40,20', "Londres");
      DrawHL("MS_LON_H", g_lon_high, clrGold, "London H");
      DrawHL("MS_LON_L", g_lon_low,  clrGold, "London L");
   }

   // NY Early 13:30-15:00 UTC
   if(cm >= 810 && cm < 900)
   {
      if(h0 > g_ny_high || g_ny_high == 0) g_ny_high = h0;
      if(l0 < g_ny_low  || g_ny_low  == 0) g_ny_low  = l0;
   }
   if(t.hour == 15 && t.min == 0 && !g_ny_ready && g_ny_high > 0)
   {
      g_ny_ready = true;
      DrawHL("MS_NY_H", g_ny_high, clrCyan, "NY Early H");
      DrawHL("MS_NY_L", g_ny_low,  clrCyan, "NY Early L");
   }

   // =================== ESTRATEGIAS ===================

   // JUDAS — sweep de Asia, 08:00-09:30 UTC
   if(g_asia_ready && !g_sig_judas && cm >= 480 && cm < 570)
   {
      if(c2 > g_asia_high && c1 < g_asia_high)
      {
         double sl = h1 + 5 * pip;
         if(EmitSignal("Judas", false, bar0, c1, sl, c1 - (sl - c1) * InpRR_Ratio, atr))
            g_sig_judas = true;
      }
      else if(c2 < g_asia_low && c1 > g_asia_low)
      {
         double sl = l1 - 5 * pip;
         if(EmitSignal("Judas", true, bar0, c1, sl, c1 + (c1 - sl) * InpRR_Ratio, atr))
            g_sig_judas = true;
      }
   }

   // LONDON CLOSE — sweep en cierre de Londres, 12:30-13:30 UTC
   if(g_lon_high > 0 && !g_sig_lonclose && cm >= 750 && cm < 810)
   {
      if(c2 > g_lon_high && c1 < g_lon_high)
      {
         double sl = h1 + 5 * pip;
         if(EmitSignal("LonClose", false, bar0, c1, sl, c1 - (sl - c1) * InpRR_Ratio, atr))
            g_sig_lonclose = true;
      }
      else if(c2 < g_lon_low && c1 > g_lon_low)
      {
         double sl = l1 - 5 * pip;
         if(EmitSignal("LonClose", true, bar0, c1, sl, c1 + (c1 - sl) * InpRR_Ratio, atr))
            g_sig_lonclose = true;
      }
   }

   // VENOM — sweep de Londres en sesión NY, 14:00-15:30 UTC
   if(g_lon_ready && !g_sig_venom && cm >= 840 && cm < 930)
   {
      if(c2 > g_lon_high && c1 < g_lon_high)
      {
         double sl = h1 + 5 * pip;
         if(EmitSignal("Venom", false, bar0, c1, sl, c1 - (sl - c1) * InpRR_Ratio, atr))
            g_sig_venom = true;
      }
      else if(c2 < g_lon_low && c1 > g_lon_low)
      {
         double sl = l1 - 5 * pip;
         if(EmitSignal("Venom", true, bar0, c1, sl, c1 + (c1 - sl) * InpRR_Ratio, atr))
            g_sig_venom = true;
      }
   }

   // BERND — bounce en rango global, 13:30-14:30 UTC
   if(!g_sig_bernd && cm >= 810 && cm < 870)
   {
      double gbh = (g_lon_high > 0) ? MathMax(g_asia_high, g_lon_high) : g_asia_high;
      double gbl = (g_lon_low  > 0) ? MathMin(g_asia_low,  g_lon_low)  : g_asia_low;
      if(gbh > 0 && gbl > 0)
      {
         if(c2 < gbl && c1 > gbl)
         {
            double sl = l1 - 5 * pip;
            if(EmitSignal("Bernd", true, bar0, c1, sl, c1 + (c1 - sl) * InpRR_Ratio, atr))
               g_sig_bernd = true;
         }
         else if(c2 > gbh && c1 < gbh)
         {
            double sl = h1 + 5 * pip;
            if(EmitSignal("Bernd", false, bar0, c1, sl, c1 - (sl - c1) * InpRR_Ratio, atr))
               g_sig_bernd = true;
         }
      }
   }

   // SILVER BULLET — sweep de NY Early, 15:00-16:00 UTC
   if(g_ny_ready && !g_sig_silver && cm >= 900 && cm < 960)
   {
      if(c2 > g_ny_high && c1 < g_ny_high)
      {
         double sl = h1 + 5 * pip;
         if(EmitSignal("SilverBullet", false, bar0, c1, sl, c1 - (sl - c1) * InpRR_Ratio, atr))
            g_sig_silver = true;
      }
      else if(c2 < g_ny_low && c1 > g_ny_low)
      {
         double sl = l1 - 5 * pip;
         if(EmitSignal("SilverBullet", true, bar0, c1, sl, c1 + (c1 - sl) * InpRR_Ratio, atr))
            g_sig_silver = true;
      }
   }

   // CRT — Candle Range Theory (HTF configurable, default H4)
   ProcessCRT(bar0, c1, h1, l1, atr);

   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| CRT — Candle Range Theory                                        |
//|  1. Rango = high/low de la última vela HTF CERRADA              |
//|  2. Barrido = M5 supera un extremo del rango                    |
//|  3. Confirmación = M5 cierra de vuelta DENTRO del rango         |
//|  4. Plan = Entry(c1) | SL(wick ± ATRbuf) | TP(extremo opuesto) |
//+------------------------------------------------------------------+
void ProcessCRT(datetime bar0, double c1, double h1, double l1, double atr_m5)
{
   // Datos HTF de vela cerrada (índice 1, sin lookahead)
   double   htf_h = iHigh(_Symbol, InpCRT_HTF, 1);
   double   htf_l = iLow(_Symbol,  InpCRT_HTF, 1);
   datetime htf_t = iTime(_Symbol, InpCRT_HTF, 1);
   if(htf_h <= 0 || htf_l <= 0) return;

   // Nueva vela HTF → resetear estado CRT
   if(htf_t != g_crt.htf_bar_time)
   {
      g_crt.htf_high     = htf_h;
      g_crt.htf_low      = htf_l;
      g_crt.htf_bar_time = htf_t;
      g_crt.swept_high   = false;
      g_crt.swept_low    = false;
      g_crt.confirmed    = false;
      g_crt.plan_active  = false;
      g_crt.sweep_wick      = 0;
      g_crt.sweep_bar_index = -1;
      g_crt.signals_emitted = 0;
      g_sig_crt             = false;
      DrawCRTRange(htf_h, htf_l);
   }
   if(g_crt.htf_high <= 0) return;

   // Filtro tamaño mínimo del rango
   double atr_htf_buf[1];
   if(CopyBuffer(g_h_atr_htf, 0, 1, 1, atr_htf_buf) < 1) return;
   if((g_crt.htf_high - g_crt.htf_low) < InpCRT_RangeMin * atr_htf_buf[0]) return;

   // Si ya confirmó, solo puede re-armarse con un sweep más profundo.
   if(g_sig_crt && (!InpCRT_ReArm || g_crt.signals_emitted >= InpCRT_MaxSignalsPerRange)) return;

   // --- FASE 1: Detectar barrido (en barra ya cerrada) ---
   if(!g_crt.swept_high && !g_crt.swept_low)
   {
      if(h1 > g_crt.htf_high)
      {
         g_crt.swept_high = true;
         g_crt.sweep_wick      = h1;
         g_crt.sweep_bar_index = 0;
         g_crt.bull             = false;  // barrió high → SHORT (entrega hacia low)
         DrawSweepMark(bar0, h1, false);
      }
      else if(l1 < g_crt.htf_low)
      {
         g_crt.swept_low  = true;
         g_crt.sweep_wick      = l1;
         g_crt.sweep_bar_index = 0;
         g_crt.bull             = true;   // barrió low → LONG (entrega hacia high)
         DrawSweepMark(bar0, l1, true);
      }
      return; // esperamos confirmación
   }

   // Expiración: el sweep debe confirmarse dentro de N velas M5.
   if(!g_crt.confirmed && g_crt.sweep_bar_index >= 0)
   {
      if(g_crt.sweep_bar_index >= InpCRT_MaxConfirmBars)
      {
         g_crt.swept_high = false;
         g_crt.swept_low  = false;
         g_crt.sweep_wick = 0;
         g_crt.sweep_bar_index = -1;
         return;
      }
      g_crt.sweep_bar_index++;
   }

   // Re-arm: barrido más profundo después de confirmar.
   if(InpCRT_ReArm && g_crt.confirmed &&
      g_crt.signals_emitted < InpCRT_MaxSignalsPerRange)
   {
      if(g_crt.bull && l1 < g_crt.sweep_wick)
      {
         g_crt.sweep_wick      = l1;
         g_crt.sweep_bar_index = 0;
         g_crt.confirmed       = false;
         g_sig_crt             = false;
         DrawSweepMark(bar0, l1, true);
         return;
      }
      else if(!g_crt.bull && h1 > g_crt.sweep_wick)
      {
         g_crt.sweep_wick      = h1;
         g_crt.sweep_bar_index = 0;
         g_crt.confirmed       = false;
         g_sig_crt             = false;
         DrawSweepMark(bar0, h1, false);
         return;
      }
   }

   if(g_crt.confirmed) return;

   // --- FASE 2: Confirmación — c1 cierra DENTRO del rango ---
   if(c1 <= g_crt.htf_low || c1 >= g_crt.htf_high) return;

   // Descartar outside bar (barrió ambos lados — ambiguo)
   if(g_crt.bull  && h1 > g_crt.htf_high) return;
   if(!g_crt.bull && l1 < g_crt.htf_low)  return;

   // --- FASE 3: Calcular plan ---
   double entry = c1;
   double sl, tp;

   if(g_crt.bull)
   {
      sl = g_crt.sweep_wick - InpCRT_ATRBuf * atr_m5;
      tp = g_crt.htf_high;
   }
   else
   {
      sl = g_crt.sweep_wick + InpCRT_ATRBuf * atr_m5;
      tp = g_crt.htf_low;
   }

   // Filtro R:R mínimo
   double risk   = MathAbs(entry - sl);
   double reward = MathAbs(tp - entry);
   if(risk <= 0 || (reward / risk) < InpCRT_RR_Min)
   {
      Print(StringFormat("[CRT] R:R %.2f < mínimo %.2f — sin señal", reward / risk, InpCRT_RR_Min));
      return;
   }

   // Gate coherencia — entry dentro del rango y lado correcto del SL
   if(g_crt.bull  && (entry <= sl || entry >= g_crt.htf_high)) return;
   if(!g_crt.bull && (entry >= sl || entry <= g_crt.htf_low))  return;

   // --- FASE 4: Emitir señal ---
   g_crt.confirmed   = true;
   g_crt.entry       = entry;
   g_crt.sl          = sl;
   g_crt.tp          = tp;
   g_crt.plan_active = true;
   g_crt.plan_start  = bar0;

   Print(StringFormat("[CRT] ✓ %s | E:%.5f SL:%.5f TP:%.5f | R:R:%.2f",
      g_crt.bull ? "LONG" : "SHORT", entry, sl, tp, reward / risk));

   DrawCRTPlan(bar0, entry, sl, tp, g_crt.bull);
   if(EmitSignal("CRT", g_crt.bull, bar0, entry, sl, tp, atr_m5))
   {
      g_crt.signals_emitted++;
      g_sig_crt = true;
   }
   else
   {
      g_crt.confirmed = false;
      g_crt.plan_active = false;
   }
}

//+------------------------------------------------------------------+
//| RIESGO & EJECUCIÓN                                               |
//+------------------------------------------------------------------+

// Usa EQUITY (no balance) para contemplar pérdidas flotantes
bool DailyLossHit()
{
   return (g_equity_start_day - AccountInfoDouble(ACCOUNT_EQUITY)) >= InpMaxLossDay;
}

// Filtra por Magic Number — solo cuenta operaciones de ESTE EA
int CountOpenTrades()
{
   int c = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket))
         if(PositionGetString(POSITION_SYMBOL)  == _Symbol &&
            PositionGetInteger(POSITION_MAGIC)  == (long)InpMagic)
            c++;
   }
   return c;
}

double CalcLot(double entry, double sl_price)
{
   double dist = MathAbs(entry - sl_price);
   if(dist <= 0) return 0;

   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || ts <= 0) return 0;

   double raw_lot = InpRiskUSD / ((dist / ts) * tv);
   double lmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double lmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lstp = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(lmin <= 0 || lmax <= 0 || lstp <= 0) return 0;

   double min_risk = (dist / ts) * tv * lmin;
   if(min_risk > InpRiskUSD * 1.10)
   {
      Print(StringFormat("[RISK] Volumen mínimo implica $%.2f > objetivo $%.2f", min_risk, InpRiskUSD));
      return 0;
   }

   double lot = MathMin(lmax, raw_lot);
   lot = MathFloor(lot / lstp) * lstp;
   if(lot < lmin) lot = lmin;

   int vol_digits = 0;
   double step_tmp = lstp;
   while(vol_digits < 8 && MathAbs(step_tmp - MathRound(step_tmp)) > 1e-10)
   {
      step_tmp *= 10.0;
      vol_digits++;
   }
   lot = NormalizeDouble(lot, vol_digits);

   double real_risk = (dist / ts) * tv * lot;
   if(real_risk > InpRiskUSD * 1.10)
   {
      Print(StringFormat("[RISK] Riesgo real $%.2f > objetivo $%.2f", real_risk, InpRiskUSD));
      return 0;
   }
   return lot;
}

double EstimatePositionRisk(ulong ticket)
{
   if(!PositionSelectByTicket(ticket)) return 0;
   if(PositionGetString(POSITION_SYMBOL) != _Symbol) return 0;
   if(PositionGetInteger(POSITION_MAGIC) != (long)InpMagic) return 0;
   double open = PositionGetDouble(POSITION_PRICE_OPEN);
   double sl   = PositionGetDouble(POSITION_SL);
   double vol  = PositionGetDouble(POSITION_VOLUME);
   if(sl <= 0 || vol <= 0) return 0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || ts <= 0) return 0;
   return MathAbs(open - sl) / ts * tv * vol;
}

double CurrentOpenRiskUSD()
{
   double total = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0) total += EstimatePositionRisk(ticket);
   }
   return total;
}

// Verifica distancia mínima al precio (stops level del broker)
bool CheckStopsLevel(double entry, double sl, double tp, bool bull)
{
   long   stops_lvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double min_dist  = stops_lvl * _Point;
   if(min_dist <= 0) return true;  // broker sin restricción
   double ref = bull ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                     : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(MathAbs(sl - ref) < min_dist) { Print("[SL] demasiado cerca del precio (stops level)"); return false; }
   if(MathAbs(tp - ref) < min_dist) { Print("[TP] demasiado cerca del precio (stops level)"); return false; }
   return true;
}

bool EmitSignal(string strat, bool bull, datetime t,
                double entry, double sl, double tp, double atr)
{
   if(DailyLossHit())
      { Print("[", strat, "] Stop diario alcanzado."); return false; }
   if(CountOpenTrades() >= InpMaxTrades)
      { Print("[", strat, "] Máximo de operaciones abiertas."); return false; }

   // Filtro spread
   double spread     = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread_pts = spread / _Point;
   if(spread_pts > InpMaxSpreadPts)
      { Print("[", strat, "] Spread alto: ", DoubleToString(spread_pts, 1), " pts"); return false; }

   // Validar stops level
   if(!CheckStopsLevel(entry, sl, tp, bull)) return false;

   // Coherencia básica SL/TP
   if(bull  && (sl >= entry || tp <= entry)) { Print("[", strat, "] SL/TP incoherente LONG");  return false; }
   if(!bull && (sl <= entry || tp >= entry)) { Print("[", strat, "] SL/TP incoherente SHORT"); return false; }

   double lot = CalcLot(entry, sl);
   if(lot <= 0) { Print("[", strat, "] Lote inválido"); return false; }

   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || ts <= 0) return false;
   double new_risk_usd = MathAbs(entry - sl) / ts * tv * lot;
   double current_risk = CurrentOpenRiskUSD();
   if(current_risk + new_risk_usd > InpMaxOpenRiskUSD + 1e-8)
   {
      Print(StringFormat("[%s] Riesgo abierto: $%.2f + $%.2f > máximo $%.2f",
         strat, current_risk, new_risk_usd, InpMaxOpenRiskUSD));
      return false;
   }

   Print(StringFormat("*** [%s] %s | E:%.5f SL:%.5f TP:%.5f | Lot:%.2f Spread:%.1f",
      strat, bull ? "LONG" : "SHORT", entry, sl, tp, lot, spread_pts));

   bool ok = bull ? trade.Buy(lot,  _Symbol, 0, sl, tp, strat)
                  : trade.Sell(lot, _Symbol, 0, sl, tp, strat);
   if(!ok)
   {
      Print("ORDER ERROR: ", trade.ResultRetcode(), " — ", trade.ResultRetcodeDescription());
      return false;
   }

   // CSV
   if(g_file != INVALID_HANDLE)
   {
      MqlDateTime dt; TimeToStruct(t, dt);
      FileWrite(g_file,
         StringFormat("%04d-%02d-%02d", dt.year, dt.mon, dt.day),
         StringFormat("%02d:%02d", dt.hour, dt.min),
         strat, bull ? "LONG" : "SHORT",
         DoubleToString(entry, _Digits), DoubleToString(sl, _Digits),
         DoubleToString(tp, _Digits), DoubleToString(lot, 2),
         DoubleToString(spread_pts, 1), DoubleToString(atr, _Digits));
      FileFlush(g_file);
   }

   // Marcas en chart
   g_obj_count++;
   string base = StringFormat("MS_%s_%d", strat, g_obj_count);
   ObjectCreate(0, base + "_A", OBJ_ARROW, 0, t, entry);
   ObjectSetInteger(0, base + "_A", OBJPROP_ARROWCODE, bull ? 233 : 234);
   ObjectSetInteger(0, base + "_A", OBJPROP_COLOR,     bull ? clrLime : clrRed);
   ObjectSetInteger(0, base + "_A", OBJPROP_WIDTH, 3);
   double off = (bull ? -8 : 8) * _Point * 10;
   ObjectCreate(0, base + "_T", OBJ_TEXT, 0, t, entry + off);
   ObjectSetString(0, base + "_T", OBJPROP_TEXT, strat + (bull ? " ▲" : " ▼"));
   ObjectSetInteger(0, base + "_T", OBJPROP_COLOR, bull ? clrLime : clrRed);
   ObjectSetInteger(0, base + "_T", OBJPROP_FONTSIZE, 8);
   ObjectSetString(0, base + "_T", OBJPROP_FONT, "Arial Bold");
   DrawRay(base + "_SL", t, sl, clrTomato);
   DrawRay(base + "_TP", t, tp, clrLimeGreen);
   ChartRedraw(0);
   return true;
}

//+------------------------------------------------------------------+
//| DIBUJO                                                           |
//+------------------------------------------------------------------+

// Rango HTF vivo (gris punteado + 50% dorado)
void DrawCRTRange(double h, double l)
{
   // Limpiar anteriores
   ObjectDelete(0, "MS_CRT_H");
   ObjectDelete(0, "MS_CRT_L");
   ObjectDelete(0, "MS_CRT_MID");

   ObjectCreate(0, "MS_CRT_H", OBJ_HLINE, 0, 0, h);
   ObjectSetInteger(0, "MS_CRT_H", OBJPROP_COLOR, clrSilver);
   ObjectSetInteger(0, "MS_CRT_H", OBJPROP_STYLE, STYLE_DASH);
   ObjectSetString(0,  "MS_CRT_H", OBJPROP_TOOLTIP, "CRT HTF High (liquidez arriba)");

   ObjectCreate(0, "MS_CRT_L", OBJ_HLINE, 0, 0, l);
   ObjectSetInteger(0, "MS_CRT_L", OBJPROP_COLOR, clrSilver);
   ObjectSetInteger(0, "MS_CRT_L", OBJPROP_STYLE, STYLE_DASH);
   ObjectSetString(0,  "MS_CRT_L", OBJPROP_TOOLTIP, "CRT HTF Low (liquidez abajo)");

   ObjectCreate(0, "MS_CRT_MID", OBJ_HLINE, 0, 0, (h + l) / 2.0);
   ObjectSetInteger(0, "MS_CRT_MID", OBJPROP_COLOR, clrGold);
   ObjectSetInteger(0, "MS_CRT_MID", OBJPROP_STYLE, STYLE_DOT);
   ObjectSetString(0,  "MS_CRT_MID", OBJPROP_TOOLTIP, "CRT 50% (imán)");
}

// Diamante en el punto de barrido
void DrawSweepMark(datetime t, double price, bool bull)
{
   g_obj_count++;
   string nm = StringFormat("MS_CRT_SWP_%d", g_obj_count);
   ObjectCreate(0, nm, OBJ_ARROW, 0, t, price);
   ObjectSetInteger(0, nm, OBJPROP_ARROWCODE, 168);   // diamante
   ObjectSetInteger(0, nm, OBJPROP_COLOR, clrViolet);
   ObjectSetInteger(0, nm, OBJPROP_WIDTH, 2);
   string nt = nm + "_T";
   ObjectCreate(0, nt, OBJ_TEXT, 0, t, price + (bull ? -14 : 14) * _Point * 10);
   ObjectSetString(0,  nt, OBJPROP_TEXT, "BARRIDO");
   ObjectSetInteger(0, nt, OBJPROP_COLOR, clrViolet);
   ObjectSetInteger(0, nt, OBJPROP_FONTSIZE, 7);
}

// Cajas del plan CRT: beige (reward) + gris (riesgo)
void DrawCRTPlan(datetime t, double entry, double sl, double tp, bool bull)
{
   g_obj_count++;
   datetime t2 = t + 20 * PeriodSeconds(PERIOD_H1);

   string nr = StringFormat("MS_CRT_TPZ_%d", g_obj_count);
   ObjectCreate(0, nr, OBJ_RECTANGLE, 0, t, entry, t2, tp);
   ObjectSetInteger(0, nr, OBJPROP_COLOR, C'210,190,140');
   ObjectSetInteger(0, nr, OBJPROP_FILL,  true);
   ObjectSetInteger(0, nr, OBJPROP_BACK,  true);
   ObjectSetString(0,  nr, OBJPROP_TOOLTIP, "CRT Reward Zone");

   string ns = StringFormat("MS_CRT_SLZ_%d", g_obj_count);
   ObjectCreate(0, ns, OBJ_RECTANGLE, 0, t, entry, t2, sl);
   ObjectSetInteger(0, ns, OBJPROP_COLOR, C'80,80,80');
   ObjectSetInteger(0, ns, OBJPROP_FILL,  true);
   ObjectSetInteger(0, ns, OBJPROP_BACK,  true);
   ObjectSetString(0,  ns, OBJPROP_TOOLTIP, "CRT Risk Zone");
}

void CreateCornerLabel()
{
   string n = "MS_TREND_LBL";
   if(ObjectFind(0, n) < 0) ObjectCreate(0, n, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, n, OBJPROP_CORNER,    CORNER_LEFT_UPPER);
   ObjectSetInteger(0, n, OBJPROP_XDISTANCE, 12);
   ObjectSetInteger(0, n, OBJPROP_YDISTANCE, 28);
   ObjectSetInteger(0, n, OBJPROP_FONTSIZE,  10);
   ObjectSetString(0,  n, OBJPROP_FONT, "Arial Bold");
   ObjectSetString(0,  n, OBJPROP_TEXT, "v3.00");
}

void UpdateTrendLabel(double close, double ema200)
{
   string n = "MS_TREND_LBL";
   if(ObjectFind(0, n) < 0) CreateCornerLabel();
   datetime now_utc = ServerTimeToUTC(TimeCurrent());
   MqlDateTime t; TimeToStruct(now_utc, t);
   int    cm  = t.hour * 60 + t.min;
   string ses = cm < 480 ? "ASIA" : cm < 810 ? "LONDRES" : cm < 1320 ? "NY" : "-";
   ObjectSetString(0,  n, OBJPROP_TEXT,
      (close > ema200 ? "↑ ALCISTA" : "↓ BAJISTA") + "  |  " + ses + "  |  v3.00 (UTC)");
   ObjectSetInteger(0, n, OBJPROP_COLOR, close > ema200 ? clrLime : clrTomato);
}

void DrawRect(string name, datetime t1, datetime t2,
              double h, double l, color clr, string lbl)
{
   if(ObjectFind(0, name) >= 0) ObjectDelete(0, name);
   ObjectCreate(0, name, OBJ_RECTANGLE, 0, t1, h, t2, l);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_FILL,  true);
   ObjectSetInteger(0, name, OBJPROP_BACK,  true);
   ObjectSetString(0,  name, OBJPROP_TOOLTIP, lbl);
}

void DrawHL(string name, double price, color clr, string lbl)
{
   if(ObjectFind(0, name) >= 0) ObjectDelete(0, name);
   ObjectCreate(0, name, OBJ_HLINE, 0, 0, price);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DASH);
   ObjectSetString(0,  name, OBJPROP_TOOLTIP, lbl + ": " + DoubleToString(price, _Digits));
}

void DrawRay(string name, datetime t, double price, color clr)
{
   if(ObjectFind(0, name) >= 0) ObjectDelete(0, name);
   ObjectCreate(0, name, OBJ_TREND, 0, t, price, t + 4 * 3600, price);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_DOT);
   ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, true);
}

void DailyReset()
{
   // Sesiones
   g_asia_high = 0; g_asia_low = 0; g_asia_ready = false; g_asia_start = 0;
   g_lon_high  = 0; g_lon_low  = 0; g_lon_ready  = false; g_lon_start  = 0;
   g_ny_high   = 0; g_ny_low   = 0; g_ny_ready   = false;
   // Flags estrategia
   g_sig_judas = false; g_sig_venom    = false; g_sig_bernd  = false;
   g_sig_lonclose = false; g_sig_silver = false; g_sig_crt   = false;
   // CRT
   ZeroMemory(g_crt);
   // Riesgo — equity del día nuevo
   g_equity_start_day = AccountInfoDouble(ACCOUNT_EQUITY);
   // Chart
   ObjectsDeleteAll(0, "MS_");
   CreateCornerLabel();
   Print("0031 v3.00 reset diario | Equity: $", DoubleToString(g_equity_start_day, 2));
}
//+------------------------------------------------------------------+