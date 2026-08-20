//+------------------------------------------------------------------+
//| EventStudyExtractor.mq5                                          |
//| Extrae releases NFP + CPI m/m (US) 2018.01-2025.12 desde el      |
//| calendario economico de MT5, para el event study NFP/CPI ->      |
//| EURUSD (marco "EURUSD Event Study - sorpresa macro", 2026-08-05).|
//|                                                                    |
//| Escalado validado empiricamente contra macro_calendar_check.csv /|
//| nfp_calendar_check.csv (2026-08-05): raw/10^6 de forma UNIFORME  |
//| para todos los eventos (NFP jul-2018: 213000000/1e6=213, coincide|
//| con 213K empleos reales; CPI m/m mar-2018: 200000/1e6=0.2,       |
//| coincide con 0.2% real). El escalado por MathPow(10,digits) de   |
//| los scripts exploratorios previos (NFP_CalendarCheck.mq5,        |
//| MacroCalendarCheck.mq5) era incorrecto -- no se reutiliza.       |
//|                                                                    |
//| Nombres de evento exactos (confirmados en macro_calendar_check.csv|
//| / nfp_calendar_check.csv, existen como filas propias distintas de |
//| "ADP Nonfarm Employment Change", "Core CPI m/m", "CPI n.s.a. m/m",|
//| etc.): "Nonfarm Payrolls" y "CPI m/m".                            |
//+------------------------------------------------------------------+
#property strict

#define ESCALA 1000000.0

datetime DesdeFecha(int y, int m, int d)
{
   return StringToTime(StringFormat("%04d.%02d.%02d", y, m, d));
}

bool EsEventoObjetivo(const string nombre)
{
   return (nombre == "Nonfarm Payrolls" || nombre == "CPI m/m");
}

void OnStart()
{
   int handle = FileOpen("event_study_releases.csv", FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ',');
   if(handle == INVALID_HANDLE)
   {
      Print("ERROR: no se pudo crear CSV. Codigo: ", GetLastError());
      return;
   }
   FileWrite(handle, "date", "time", "event", "actual", "forecast", "prev", "surprise");

   int total_filas = 0;
   int total_descartadas_null = 0;

   int anio_desde = 2018, anio_hasta = 2025;

   for(int anio = anio_desde; anio <= anio_hasta; anio++)
   {
      for(int mes = 1; mes <= 12; mes++)
      {
         datetime desde = DesdeFecha(anio, mes, 1);
         datetime hasta = (mes == 12) ? DesdeFecha(anio + 1, 1, 1) : DesdeFecha(anio, mes + 1, 1);

         MqlCalendarValue valores[];
         int total = CalendarValueHistory(valores, desde, hasta, "US", NULL);
         if(total <= 0)
            continue;

         for(int j = 0; j < total; j++)
         {
            MqlCalendarEvent evento;
            if(!CalendarEventById(valores[j].event_id, evento))
               continue;

            if(!EsEventoObjetivo(evento.name))
               continue;

            if(valores[j].forecast_value == LONG_MIN)
            {
               total_descartadas_null++;
               continue;
            }

            double actual   = valores[j].actual_value   / ESCALA;
            double forecast = valores[j].forecast_value / ESCALA;
            double prev     = (valores[j].prev_value == LONG_MIN) ? EMPTY_VALUE : valores[j].prev_value / ESCALA;
            double surprise = (valores[j].actual_value - valores[j].forecast_value) / ESCALA;

            FileWrite(handle,
               TimeToString(valores[j].time, TIME_DATE),
               TimeToString(valores[j].time, TIME_MINUTES),
               evento.name,
               DoubleToString(actual, 6),
               DoubleToString(forecast, 6),
               (prev == EMPTY_VALUE) ? "" : DoubleToString(prev, 6),
               DoubleToString(surprise, 6)
            );
            total_filas++;
         }
      }
   }

   FileClose(handle);
   Print("EventStudyExtractor: ", total_filas, " filas escritas (", total_descartadas_null,
         " descartadas por forecast_value nulo). CSV: Common\\Files\\event_study_releases.csv");
}
