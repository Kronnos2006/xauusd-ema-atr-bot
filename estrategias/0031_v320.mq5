//+------------------------------------------------------------------+
//| 0031.mq5  v3.21                                                  |
//| Judas | Venom | Bernd | LonClose | SilverBullet | CRT           |
//|                                                                  |
//| v3.21 vs v3.20: InpRiskUSD ($ fijo) -> InpRiskPct (% de equity   |
//|  actual). Motivo: en el batch de 7 backtests (2005-2015) CRT     |
//|  arruinó la cuenta de $100 en 2005 con riesgo fijo de $1/trade,  |
//|  y quedó sin poder operar los 9 años restantes (margen           |
//|  insuficiente) — la muestra real terminó siendo solo unos meses, |
//|  no 10 años. Con riesgo en %, el $ arriesgado por trade se       |
//|  reduce junto con la equity en una racha perdedora.              |
//|                                                                  |
//| v3.20 — framework de investigación (aislamiento por estrategia) |
//|  vs v3.10:                                                       |
//|  - Strategy Lab: InpStrategyMode aísla una sola estrategia       |
//|  - FIX: sesiones (Asia/Londres/NY) acumulaban high/low con la    |
//|    vela recién ABIERTA (índice 0, ~precio de apertura) en vez    |
//|    de la vela recién CERRADA (índice 1) -> rango de sesión       |
//|    subestimado/incorrecto para Judas/Venom/Bernd/LonClose/SB.    |
//|  - FIX: CSV etiquetaba "hora_utc" pero usaba hora de SERVIDOR    |
//|    sin convertir (bug si InpServerUTCOffset != 0).               |
//|  - FIX: CRT ya no se resetea en DailyReset() — el control de     |
//|    señales pasa a ser 100% por rango HTF (g_crt.signals_emitted),|
//|    no por día. g_sig_crt deja de participar en el reset diario.  |
//|  - CRT: Kill Zone configurable (default 08:00-18:00 UTC),        |
//|    calculada con ServerTimeToUTC(bar0), nunca con TimeGMT().     |
//|  - CRT: InpCRT_MaxSignalsPerRange default 2 -> 1.                |
//|  - CRT: cooldown real de N barras M5 (default 2) entre una       |
//|    señal/re-arm y la siguiente confirmación.                     |
//|  - Logging ampliado: una fila por operación (escrita al cierre)  |
//|    con entrada, salida, PnL, R múltiplo, MAE/MFE (resolución M5),|
//|    sesión, día de semana, hora, EMA20/200, ATR, spread, riesgo.  |
//|  - Sin cambios de arquitectura fuera de lo anterior: se preserva |
//|    g_last_bar guard, flags por estrategia, DailyReset, Magic,    |
//|    CountOpenTrades, DailyLossHit, CheckStopsLevel, EmitSignal    |
//|    bool, CalcLot con hard reject, CurrentOpenRiskUSD.            |
//+------------------------------------------------------------------+
#property copyright "Invenio 2026"
#property version   "3.21"
#property strict

#include <Trade\Trade.mqh>
CTrade trade;

//--- Strategy Lab — aísla una sola estrategia por backtest
enum ENUM_STRATEGY_MODE
{
   STRAT_ALL           = 0,
   STRAT_JUDAS         = 1,
   STRAT_VENOM         = 2,
   STRAT_BERND         = 3,
   STRAT_LONCLOSE      = 4,
   STRAT_SILVERBULLET  = 5,
   STRAT_CRT           = 6
};
input ENUM_STRATEGY_MODE InpStrategyMode = STRAT_JUDAS;  // qué estrategia(s) correr

//--- Inputs generales
input ulong  InpMagic        = 31000;
input double InpRiskPct      = 1.0;    // % de EQUITY actual arriesgado por trade (no $ fijo — evita ruina en rachas largas)
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
input int             InpCRT_MaxSignalsPerRange = 1; // máximo de señales por rango HTF
input int             InpCRT_MaxConfirmBars = 3;     // M5 máximas para confirmar sweep
input int             InpCRT_RearmCooldownBars = 2;  // M5 mínimas entre señal/re-arm y nueva confirmación
input int             InpCRT_KillZoneStart = 480;    // 08:00 UTC — inicio ventana de entrada CRT
input int             InpCRT_KillZoneEnd   = 1080;   // 18:00 UTC — fin ventana de entrada CRT

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

//--- Flags señal — máximo 1 por estrategia por día (CRT usa control propio por rango, ver g_crt)
bool g_sig_judas    = false;
bool g_sig_venom    = false;
bool g_sig_bernd    = false;
bool g_sig_lonclose = false;
bool g_sig_silver   = false;
bool g_sig_crt      = false;   // true si ya hay >=1 señal CRT confirmada en el rango HTF activo

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
   int      bars_since_last_signal;  // cooldown: barras M5 desde la última señal/re-arm (999 = sin cooldown activo)
};
CRTState g_crt;

//--- Riesgo diario
double g_equity_start_day = 0;
int    g_utc_day_key = -1;

//--- Auxiliares
int g_obj_count = 0;
int g_file      = INVALID_HANDLE;

//--- Valores de la barra actual, usados por EmitSignal para logging (evita rehacer la firma en cada call site)
double g_cur_ema20  = 0;
double g_cur_ema200 = 0;

//--- Log de operaciones abiertas — se escribe una fila completa al CSV recién al cerrar la posición
struct OpenTradeLog
{
   ulong    ticket;
   string   strategy;
   bool     bull;
   datetime entry_time;   // hora de SERVIDOR (se convierte a UTC al loguear)
   double   entry;
   double   sl;
   double   tp;
   double   lot;
   double   risk_usd;
   double   spread_pts;
   double   atr_m5;
   double   ema20;
   double   ema200;
   string   session;
   double   mae;   // adverso máximo, en precio
   double   mfe;   // favorable máximo, en precio
};
OpenTradeLog g_open_logs[];

datetime ServerTimeToUTC(datetime server_time)
{
   return server_time - (InpServerUTCOffset * 3600);
}

string SessionName(int cm)
{
   if(cm < 480)  return "ASIA";
   if(cm < 810)  return "LONDRES";
   if(cm < 1320) return "NY";
   return "OTRO";
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
   g_crt.bars_since_last_signal = 999;

   g_file = FileOpen("0031v320.csv",
      FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ',');
   if(g_file != INVALID_HANDLE)
   {
      FileSeek(g_file, 0, SEEK_END);
      if(FileTell(g_file) == 0)
         FileWrite(g_file,
            "ticket","strategy","direction","entry_time_utc",
            "entry","sl","tp","lot","risk_usd",
            "spread_pts","atr_m5","ema20","ema200",
            "session","day_of_week","hour",
            "exit_time_utc","exit_price","pnl_usd","r_multiple","win_loss",
            "mae","mfe");
   }

   CreateCornerLabel();
   Print("0031 v3.21 OK | Modo:", EnumToString(InpStrategyMode),
         " | Magic:", InpMagic, " | Símbolo:", _Symbol, " | UTC offset:", InpServerUTCOffset);
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Volcar al CSV cualquier operación que siga abierta al terminar (backtest o EA detenido)
   for(int i = 0; i < ArraySize(g_open_logs); i++)
      WriteExitLog(g_open_logs[i]);

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

   // Precios (barra cerrada = índice 1). Toda la lógica de señales y de
   // acumulación de rango de sesión usa SOLO la vela ya cerrada — nunca
   // la vela en formación (índice 0), que en el guard "una vez por barra"
   // apenas tiene un tick y no representa el rango real de esa vela.
   double c1 = iClose(_Symbol, PERIOD_M5, 1);
   double c2 = iClose(_Symbol, PERIOD_M5, 2);
   double h1 = iHigh(_Symbol,  PERIOD_M5, 1);
   double l1 = iLow(_Symbol,   PERIOD_M5, 1);
   double pip = _Point * 10;

   // ATR M5
   double atr_buf[1];
   if(CopyBuffer(g_h_atr14, 0, 1, 1, atr_buf) < 1) return;
   double atr = atr_buf[0];

   // EMAs
   double e20[1], e200[1];
   if(CopyBuffer(g_h_ema20,  0, 1, 1, e20)  < 1) return;
   if(CopyBuffer(g_h_ema200, 0, 1, 1, e200) < 1) return;
   g_cur_ema20  = e20[0];
   g_cur_ema200 = e200[0];
   UpdateTrendLabel(c1, e200[0]);

   // Mantenimiento de operaciones abiertas: MAE/MFE (resolución M5, con la
   // vela ya cerrada) y volcado a CSV de las que se cerraron desde la última barra.
   UpdateOpenTradeLogs(h1, l1);

   // =================== SESIONES ===================
   // FIX vs v3.10: se acumulaba con h0/l0 (vela recién abierta, ~precio de
   // apertura) en vez de h1/l1 (vela recién cerrada) -> el rango de sesión
   // quedaba subestimado y no reflejaba el high/low real intra-vela.

   // Asia 00:00-08:00 UTC
   if(cm >= 0 && cm < 480)
   {
      if(g_asia_start == 0) g_asia_start = bar0;
      if(h1 > g_asia_high || g_asia_high == 0) g_asia_high = h1;
      if(l1 < g_asia_low  || g_asia_low  == 0) g_asia_low  = l1;
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
      if(h1 > g_lon_high || g_lon_high == 0) g_lon_high = h1;
      if(l1 < g_lon_low  || g_lon_low  == 0) g_lon_low  = l1;
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
      if(h1 > g_ny_high || g_ny_high == 0) g_ny_high = h1;
      if(l1 < g_ny_low  || g_ny_low  == 0) g_ny_low  = l1;
   }
   if(t.hour == 15 && t.min == 0 && !g_ny_ready && g_ny_high > 0)
   {
      g_ny_ready = true;
      DrawHL("MS_NY_H", g_ny_high, clrCyan, "NY Early H");
      DrawHL("MS_NY_L", g_ny_low,  clrCyan, "NY Early L");
   }

   // =================== ESTRATEGIAS (Strategy Lab) ===================
   bool runAll = (InpStrategyMode == STRAT_ALL);

   // JUDAS — sweep de Asia, 08:00-09:30 UTC
   if((runAll || InpStrategyMode == STRAT_JUDAS) &&
      g_asia_ready && !g_sig_judas && cm >= 480 && cm < 570)
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
   if((runAll || InpStrategyMode == STRAT_LONCLOSE) &&
      g_lon_high > 0 && !g_sig_lonclose && cm >= 750 && cm < 810)
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
   if((runAll || InpStrategyMode == STRAT_VENOM) &&
      g_lon_ready && !g_sig_venom && cm >= 840 && cm < 930)
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
   if((runAll || InpStrategyMode == STRAT_BERND) &&
      !g_sig_bernd && cm >= 810 && cm < 870)
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
   if((runAll || InpStrategyMode == STRAT_SILVERBULLET) &&
      g_ny_ready && !g_sig_silver && cm >= 900 && cm < 960)
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
   if(runAll || InpStrategyMode == STRAT_CRT)
      ProcessCRT(bar0, cm, c1, h1, l1, atr);

   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| CRT — Candle Range Theory                                        |
//|  1. Rango = high/low de la última vela HTF CERRADA              |
//|  2. Barrido = M5 supera un extremo del rango                    |
//|  3. Confirmación = M5 cierra de vuelta DENTRO del rango         |
//|     (solo dentro de la Kill Zone y fuera del cooldown de re-arm)|
//|  4. Plan = Entry(c1) | SL(wick ± ATRbuf) | TP(extremo opuesto) |
//|                                                                  |
//|  Control de señales: 100% por rango HTF vía g_crt.signals_emitted|
//|  y g_crt.htf_bar_time. NO depende de DailyReset() ni de day_key. |
//+------------------------------------------------------------------+
void ProcessCRT(datetime bar0, int cm, double c1, double h1, double l1, double atr_m5)
{
   // Datos HTF de vela cerrada (índice 1, sin lookahead)
   double   htf_h = iHigh(_Symbol, InpCRT_HTF, 1);
   double   htf_l = iLow(_Symbol,  InpCRT_HTF, 1);
   datetime htf_t = iTime(_Symbol, InpCRT_HTF, 1);
   if(htf_h <= 0 || htf_l <= 0) return;

   // Nueva vela HTF → resetear estado CRT (único disparador de reset — no el día calendario)
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
      g_crt.bars_since_last_signal = 999;
      g_sig_crt             = false;
      DrawCRTRange(htf_h, htf_l);
   }
   if(g_crt.htf_high <= 0) return;

   if(g_crt.bars_since_last_signal < 999) g_crt.bars_since_last_signal++;

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
         g_crt.bars_since_last_signal = 0;
         g_sig_crt             = false;
         DrawSweepMark(bar0, l1, true);
         return;
      }
      else if(!g_crt.bull && h1 > g_crt.sweep_wick)
      {
         g_crt.sweep_wick      = h1;
         g_crt.sweep_bar_index = 0;
         g_crt.confirmed       = false;
         g_crt.bars_since_last_signal = 0;
         g_sig_crt             = false;
         DrawSweepMark(bar0, h1, false);
         return;
      }
   }

   if(g_crt.confirmed) return;

   // Cooldown real: mínimo InpCRT_RearmCooldownBars M5 desde la última señal/re-arm.
   // Vive fuera de g_sig_crt/g_crt.confirmed a propósito para que no lo neutralice
   // ningún otro flag — es la única condición que gatea este chequeo.
   if(g_crt.bars_since_last_signal < InpCRT_RearmCooldownBars) return;

   // Kill Zone — CRT no opera 24/7: solo confirma/entra dentro de la ventana UTC.
   // El rango y el barrido se siguen rastreando fuera de la ventana; lo único
   // que se bloquea aquí es la apertura de operación.
   if(cm < InpCRT_KillZoneStart || cm >= InpCRT_KillZoneEnd) return;

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
      g_crt.bars_since_last_signal = 0;
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

   // Riesgo objetivo = % de la EQUITY actual, no un $ fijo. Con $ fijo, una
   // racha perdedora deja el riesgo por trade cada vez más grande en términos
   // relativos hasta que el margen no alcanza ni para el lote mínimo (ruina
   // temprana que trunca la muestra — visto en CRT: cuenta reventada en 2005,
   // sin datos reales de los 9 años restantes). Al ser %, el riesgo en $ se
   // reduce junto con la equity, evitando ese colapso.
   double riskUSD = AccountInfoDouble(ACCOUNT_EQUITY) * (InpRiskPct / 100.0);
   if(riskUSD <= 0) return 0;

   double raw_lot = riskUSD / ((dist / ts) * tv);
   double lmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double lmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lstp = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(lmin <= 0 || lmax <= 0 || lstp <= 0) return 0;

   double min_risk = (dist / ts) * tv * lmin;
   if(min_risk > riskUSD * 1.10)
   {
      Print(StringFormat("[RISK] Volumen mínimo implica $%.2f > objetivo $%.2f", min_risk, riskUSD));
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
   if(real_risk > riskUSD * 1.10)
   {
      Print(StringFormat("[RISK] Riesgo real $%.2f > objetivo $%.2f", real_risk, riskUSD));
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

   // El ticket de posición, en cuentas hedging, es el ticket del deal de apertura.
   // Esta EA asume hedging (CountOpenTrades/EstimatePositionRisk ya recorren
   // múltiples posiciones simultáneas por symbol+magic) — no se cambia ese supuesto.
   ulong pos_ticket = trade.ResultDeal();

   int n = ArraySize(g_open_logs);
   ArrayResize(g_open_logs, n + 1);
   g_open_logs[n].ticket     = pos_ticket;
   g_open_logs[n].strategy   = strat;
   g_open_logs[n].bull       = bull;
   g_open_logs[n].entry_time = t;
   g_open_logs[n].entry      = entry;
   g_open_logs[n].sl         = sl;
   g_open_logs[n].tp         = tp;
   g_open_logs[n].lot        = lot;
   g_open_logs[n].risk_usd   = new_risk_usd;
   g_open_logs[n].spread_pts = spread_pts;
   g_open_logs[n].atr_m5     = atr;
   g_open_logs[n].ema20      = g_cur_ema20;
   g_open_logs[n].ema200     = g_cur_ema200;
   {
      MqlDateTime dtu; TimeToStruct(ServerTimeToUTC(t), dtu);
      g_open_logs[n].session = SessionName(dtu.hour * 60 + dtu.min);
   }
   g_open_logs[n].mae = 0;
   g_open_logs[n].mfe = 0;

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
//| LOGGING — ciclo de vida de la operación                          |
//+------------------------------------------------------------------+

// Actualiza MAE/MFE (resolución M5, con la vela ya cerrada) de las posiciones
// abiertas propias, y vuelca al CSV las que ya no están abiertas (cerradas
// desde la barra anterior).
void UpdateOpenTradeLogs(double h1, double l1)
{
   for(int i = ArraySize(g_open_logs) - 1; i >= 0; i--)
   {
      if(PositionSelectByTicket(g_open_logs[i].ticket))
      {
         double favorable, adverse;
         if(g_open_logs[i].bull)
         {
            favorable = h1 - g_open_logs[i].entry;
            adverse   = g_open_logs[i].entry - l1;
         }
         else
         {
            favorable = g_open_logs[i].entry - l1;
            adverse   = h1 - g_open_logs[i].entry;
         }
         if(favorable > g_open_logs[i].mfe) g_open_logs[i].mfe = favorable;
         if(adverse   > g_open_logs[i].mae) g_open_logs[i].mae = adverse;
      }
      else
      {
         WriteExitLog(g_open_logs[i]);
         ArrayRemove(g_open_logs, i, 1);
      }
   }
}

// Escribe la fila completa (entrada + salida) de una operación al CSV.
// Si la posición sigue abierta (llamada solo desde OnDeinit), deja los
// campos de salida vacíos y marca win_loss="OPEN".
void WriteExitLog(const OpenTradeLog &log)
{
   if(g_file == INVALID_HANDLE) return;

   double   pnl        = 0;
   double   exit_price = 0;
   datetime exit_time  = 0;
   bool     found_exit = false;

   if(HistorySelectByPosition(log.ticket))
   {
      int deals = HistoryDealsTotal();
      for(int i = 0; i < deals; i++)
      {
         ulong dticket = HistoryDealGetTicket(i);
         if(dticket == 0) continue;
         pnl += HistoryDealGetDouble(dticket, DEAL_PROFIT)
              + HistoryDealGetDouble(dticket, DEAL_SWAP)
              + HistoryDealGetDouble(dticket, DEAL_COMMISSION);
         if(HistoryDealGetInteger(dticket, DEAL_ENTRY) == DEAL_ENTRY_OUT)
         {
            exit_price = HistoryDealGetDouble(dticket, DEAL_PRICE);
            exit_time  = (datetime)HistoryDealGetInteger(dticket, DEAL_TIME);
            found_exit = true;
         }
      }
   }

   double risk_dist = MathAbs(log.entry - log.sl);
   double pnl_dist  = log.bull ? (exit_price - log.entry) : (log.entry - exit_price);
   double r_mult    = (found_exit && risk_dist > 0) ? pnl_dist / risk_dist : 0;

   MqlDateTime dte; TimeToStruct(ServerTimeToUTC(log.entry_time), dte);
   string dow_names[7] = {"DOM","LUN","MAR","MIE","JUE","VIE","SAB"};

   FileWrite(g_file,
      IntegerToString((long)log.ticket), log.strategy, log.bull ? "LONG" : "SHORT",
      TimeToString(ServerTimeToUTC(log.entry_time), TIME_DATE|TIME_MINUTES),
      DoubleToString(log.entry, _Digits), DoubleToString(log.sl, _Digits), DoubleToString(log.tp, _Digits),
      DoubleToString(log.lot, 2), DoubleToString(log.risk_usd, 2),
      DoubleToString(log.spread_pts, 1), DoubleToString(log.atr_m5, _Digits),
      DoubleToString(log.ema20, _Digits), DoubleToString(log.ema200, _Digits),
      log.session, dow_names[dte.day_of_week], dte.hour,
      found_exit ? TimeToString(ServerTimeToUTC(exit_time), TIME_DATE|TIME_MINUTES) : "",
      found_exit ? DoubleToString(exit_price, _Digits) : "",
      DoubleToString(pnl, 2), DoubleToString(r_mult, 2),
      found_exit ? (pnl > 0 ? "WIN" : "LOSS") : "OPEN",
      DoubleToString(log.mae, _Digits), DoubleToString(log.mfe, _Digits));
   FileFlush(g_file);
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
   ObjectSetString(0,  n, OBJPROP_TEXT, "v3.21");
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
      (close > ema200 ? "↑ ALCISTA" : "↓ BAJISTA") + "  |  " + ses + "  |  v3.21 (UTC) | " + EnumToString(InpStrategyMode));
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
   // Flags estrategia — CRT (g_sig_crt / g_crt) NO se toca acá: su ciclo de
   // vida es 100% por rango HTF (ver ProcessCRT), no por día calendario.
   g_sig_judas = false; g_sig_venom    = false; g_sig_bernd  = false;
   g_sig_lonclose = false; g_sig_silver = false;
   // Riesgo — equity del día nuevo
   g_equity_start_day = AccountInfoDouble(ACCOUNT_EQUITY);
   // Chart
   ObjectsDeleteAll(0, "MS_");
   CreateCornerLabel();
   Print("0031 v3.21 reset diario | Equity: $", DoubleToString(g_equity_start_day, 2));
}
//+------------------------------------------------------------------+
