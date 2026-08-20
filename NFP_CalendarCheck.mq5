//+------------------------------------------------------------------+
//| NFP_CalendarCheck.mq5                                            |
//+------------------------------------------------------------------+
#property strict

datetime fechas_objetivo[] = {
   D'2010.07.02', D'2015.07.03', D'2018.07.06', D'2021.07.02', D'2024.07.05'
};

void OnStart()
{
   int handle = FileOpen("nfp_calendar_check.csv", FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ',');
   if(handle == INVALID_HANDLE)
   {
      Print("ERROR: no se pudo crear CSV. Codigo: ", GetLastError());
      return;
   }
   FileWrite(handle, "fecha_objetivo", "event_time", "event_name", "country",
             "actual_value_raw", "forecast_value_raw", "prev_value_raw",
             "digits", "actual_escalado", "forecast_escalado");

   int total_encontrados = 0;

   for(int i = 0; i < ArraySize(fechas_objetivo); i++)
   {
      datetime objetivo = fechas_objetivo[i];
      datetime desde    = objetivo - 3 * 24 * 60 * 60;
      datetime hasta    = objetivo + 3 * 24 * 60 * 60;

      MqlCalendarValue valores[];
      int total = CalendarValueHistory(valores, desde, hasta, "US", NULL);

      if(total <= 0)
      {
         Print("Sin eventos US en ", TimeToString(objetivo, TIME_DATE),
               " | GetLastError=", GetLastError());
         FileWrite(handle, TimeToString(objetivo, TIME_DATE),
                   "SIN_EVENTOS_EN_VENTANA", "", "", "", "", "", "", "");
         continue;
      }

      bool encontro = false;

      for(int j = 0; j < total; j++)
      {
         MqlCalendarEvent evento;
         if(!CalendarEventById(valores[j].event_id, evento))
            continue;

         bool es_nfp = (StringFind(evento.name, "Nonfarm")  >= 0 ||
                        StringFind(evento.name, "Non-Farm") >= 0 ||
                        StringFind(evento.name, "Payroll")  >= 0 ||
                        StringFind(evento.name, "payroll")  >= 0);
         if(!es_nfp) continue;

         encontro = true;
         total_encontrados++;

         // FIX 1: cast explicito uint -> int
         int digits = (int)evento.digits;
         double factor = MathPow(10, digits);

         // FIX 2: country_code no existe en MqlCalendarEvent
         // se obtiene via CalendarCountryById
         MqlCalendarCountry pais;
         string country_str = "N/A";
         if(CalendarCountryById(evento.country_id, pais))
            country_str = pais.code;

         FileWrite(handle,
            TimeToString(objetivo,       TIME_DATE),
            TimeToString(valores[j].time, TIME_DATE|TIME_MINUTES),
            evento.name,
            country_str,
            (string)valores[j].actual_value,
            (string)valores[j].forecast_value,
            (string)valores[j].prev_value,
            (string)digits,
            DoubleToString(valores[j].actual_value   / factor, digits),
            DoubleToString(valores[j].forecast_value / factor, digits)
         );
      }

      if(!encontro)
      {
         Print("Ventana ", TimeToString(objetivo, TIME_DATE),
               ": ", total, " eventos US pero ninguno NFP/Payroll:");
         for(int j = 0; j < total; j++)
         {
            MqlCalendarEvent ev;
            if(CalendarEventById(valores[j].event_id, ev))
               Print("  -> ", ev.name, " | ", TimeToString(valores[j].time, TIME_DATE|TIME_MINUTES));
         }
         FileWrite(handle, TimeToString(objetivo, TIME_DATE),
                   "SIN_MATCH_NOMBRE", "", "", "", "", "", "", "");
      }
   }

   FileClose(handle);
   Print("Eventos NFP encontrados: ", total_encontrados, "/5");
   Print("CSV: C:\\Users\\josem\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\nfp_calendar_check.csv");
}