//+------------------------------------------------------------------+
//|                                          Donchian20_Visual.mq5   |
//|  Solo visualizacion -- NO ejecuta ordenes, NO toca capital.      |
//|  Marca en el grafico (flecha) y en el Journal cuando el cierre   |
//|  D1 confirmado rompe el canal de 20 dias (excluyendo hoy), y     |
//|  muestra en pantalla el estado de la senal en tiempo real.       |
//+------------------------------------------------------------------+
#property copyright "Proyecto research MT5 -- solo visualizacion, sin ejecucion de ordenes"
#property version   "1.00"
#property strict

input int    DonchianPeriodo   = 20;             // dias del canal (excluyendo el dia evaluado)
input string SimboloEsperado   = "XAUUSD";
input color  ColorFlechaLong   = clrLime;
input color  ColorFlechaShort  = clrRed;
input int    TamanoFlecha      = 3;

datetime g_ultima_barra_confirmada = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(_Symbol != SimboloEsperado)
     {
      Print("Donchian20_Visual: simbolo del grafico (", _Symbol,
            ") distinto del esperado (", SimboloEsperado, "). EA no se activa.");
      return(INIT_PARAMETERS_INCORRECT);
     }
   // No se exige D1 en el grafico: todas las llamadas a datos fijan PERIOD_D1
   // explicitamente (iTime/iClose/CopyClose), asi que el canal Donchian se
   // calcula siempre sobre velas D1 sin importar el timeframe del grafico.
   if(_Period != PERIOD_D1)
      Print("Donchian20_Visual: grafico en ", EnumToString(_Period),
            ", el canal se calcula igual sobre velas D1 (dato interno, no depende del grafico).");

   Print("Donchian20_Visual inicializado -- SOLO visualizacion, no ejecuta ordenes ni toca capital. ",
         "Periodo Donchian=", DonchianPeriodo);

   g_ultima_barra_confirmada = 0;
   EvaluarSenalConfirmada();  // por si ya hay historial al arrancar, no esperar al primer cambio de barra
   ActualizarComentario();

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   Comment("");
   Print("Donchian20_Visual detenido. Razon=", reason);
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime barra_actual = iTime(_Symbol, PERIOD_D1, 0);

   if(barra_actual != g_ultima_barra_confirmada)
     {
      // Nueva barra D1 abierta => la barra anterior (shift 1) ya tiene cierre confirmado
      EvaluarSenalConfirmada();
      g_ultima_barra_confirmada = barra_actual;
     }

   ActualizarComentario();
  }

//+------------------------------------------------------------------+
//| Calcula max/min de cierres en el rango [ini, ini+periodo-1]      |
//+------------------------------------------------------------------+
bool CalcularRangoDonchian(int shift_inicio, int periodo, double &maximo, double &minimo)
  {
   double cierres[];
   ArraySetAsSeries(cierres, true);
   int copiados = CopyClose(_Symbol, PERIOD_D1, shift_inicio, periodo, cierres);
   if(copiados < periodo)
      return(false);

   maximo = cierres[ArrayMaximum(cierres)];
   minimo = cierres[ArrayMinimum(cierres)];
   return(true);
  }

//+------------------------------------------------------------------+
//| Senal CONFIRMADA: evalua el cierre de la barra que acaba de      |
//| cerrar (shift 1) contra el canal de los DonchianPeriodo dias      |
//| anteriores a ella (shift 2 .. shift 1+DonchianPeriodo).           |
//| Loguea en el Journal y dibuja una flecha una sola vez por dia.    |
//+------------------------------------------------------------------+
void EvaluarSenalConfirmada()
  {
   double maximo20, minimo20;
   if(!CalcularRangoDonchian(2, DonchianPeriodo, maximo20, minimo20))
      return; // no hay suficiente historial todavia

   double cierre_confirmado = iClose(_Symbol, PERIOD_D1, 1);
   datetime tiempo_confirmado = iTime(_Symbol, PERIOD_D1, 1);

   if(cierre_confirmado > maximo20)
     {
      PrintFormat("Donchian20_Visual [%s] LONG -- cierre %.2f > max20d %.2f (min20d %.2f)",
                  TimeToString(tiempo_confirmado, TIME_DATE), cierre_confirmado, maximo20, minimo20);
      DibujarFlecha(tiempo_confirmado, cierre_confirmado, true);
     }
   else if(cierre_confirmado < minimo20)
     {
      PrintFormat("Donchian20_Visual [%s] SHORT -- cierre %.2f < min20d %.2f (max20d %.2f)",
                  TimeToString(tiempo_confirmado, TIME_DATE), cierre_confirmado, minimo20, maximo20);
      DibujarFlecha(tiempo_confirmado, cierre_confirmado, false);
     }
   else
     {
      PrintFormat("Donchian20_Visual [%s] NEUTRAL -- cierre %.2f dentro del canal [%.2f, %.2f]",
                  TimeToString(tiempo_confirmado, TIME_DATE), cierre_confirmado, minimo20, maximo20);
     }
  }

//+------------------------------------------------------------------+
void DibujarFlecha(datetime tiempo, double precio, bool es_long)
  {
   string nombre = StringFormat("Donchian20_%s_%s", es_long ? "LONG" : "SHORT",
                                 TimeToString(tiempo, TIME_DATE));

   if(ObjectFind(0, nombre) >= 0)
      return; // ya dibujada para este dia, no duplicar

   ObjectCreate(0, nombre, es_long ? OBJ_ARROW_UP : OBJ_ARROW_DOWN, 0, tiempo, precio);
   ObjectSetInteger(0, nombre, OBJPROP_COLOR, es_long ? ColorFlechaLong : ColorFlechaShort);
   ObjectSetInteger(0, nombre, OBJPROP_WIDTH, TamanoFlecha);
   ObjectSetInteger(0, nombre, OBJPROP_ANCHOR, es_long ? ANCHOR_TOP : ANCHOR_BOTTOM);
   ObjectSetString(0, nombre, OBJPROP_TOOLTIP,
                    StringFormat("%s Donchian%d -- %s", es_long ? "LONG" : "SHORT",
                                 DonchianPeriodo, TimeToString(tiempo, TIME_DATE)));
  }

//+------------------------------------------------------------------+
//| Comment en pantalla: estado EN VIVO usando la barra en formacion  |
//| (shift 0) contra el canal de los DonchianPeriodo dias anteriores  |
//| (shift 1 .. shift DonchianPeriodo) -- distinto de la senal        |
//| confirmada que se loguea/dibuja solo al cierre del dia.           |
//+------------------------------------------------------------------+
void ActualizarComentario()
  {
   double maximo20, minimo20;
   if(!CalcularRangoDonchian(1, DonchianPeriodo, maximo20, minimo20))
     {
      Comment("Donchian20_Visual: historial insuficiente todavia (", DonchianPeriodo, " dias requeridos).");
      return;
     }

   double cierre_hoy = iClose(_Symbol, PERIOD_D1, 0);
   string senal_actual = "NEUTRAL";
   if(cierre_hoy > maximo20)
      senal_actual = "LONG";
   else if(cierre_hoy < minimo20)
      senal_actual = "SHORT";

   string texto = StringFormat(
      "Donchian20_Visual -- SOLO VISUALIZACION, sin ejecucion de ordenes\n" +
      "Fecha: %s\n" +
      "Señal actual (barra en formacion): %s\n" +
      "Cierre hoy (parcial): %.2f\n" +
      "Máximo %dd (excl. hoy): %.2f\n" +
      "Mínimo %dd (excl. hoy): %.2f",
      TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES),
      senal_actual,
      cierre_hoy,
      DonchianPeriodo, maximo20,
      DonchianPeriodo, minimo20
   );

   Comment(texto);
  }
//+------------------------------------------------------------------+
