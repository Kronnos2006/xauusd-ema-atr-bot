//+------------------------------------------------------------------+
//| MacroCalendarCheck.mq5                                           |
//| Verifica si CalendarValueHistory devuelve forecast_value historico|
//| real (no nulo = no -9223372036854775808) para CPI y FOMC Rate     |
//| Decision desde 2018. Mismo patron ya verificado en                |
//| NFP_CalendarCheck.mq5 (CalendarCountryById para el pais, cast      |
//| explicito uint->int para digits).                                 |
//+------------------------------------------------------------------+
#property strict

datetime fechas_cpi[] = {
   D'2018.03.13', D'2021.06.10', D'2024.03.12'
};

datetime fechas_fomc[] = {
   D'2018.03.21', D'2021.06.16', D'2024.03.20'
};

int handle_global;
int total_encontrados_global = 0;

void ProcesarVentana(datetime objetivo, string etiqueta_categoria,
                      bool usar_filtro_cpi)
{
   datetime desde = objetivo - 3 * 24 * 60 * 60;
   datetime hasta = objetivo + 3 * 24 * 60 * 60;

   MqlCalendarValue valores[];
   int total = CalendarValueHistory(valores, desde, hasta, "US", NULL);

   if(total <= 0)
   {
      Print("Sin eventos US en ", TimeToString(objetivo, TIME_DATE),
            " (", etiqueta_categoria, ") | GetLastError=", GetLastError());
      FileWrite(handle_global, TimeToString(objetivo, TIME_DATE), etiqueta_categoria,
                "SIN_EVENTOS_EN_VENTANA", "", "", "", "", "", "", "");
      return;
   }

   bool encontro = false;

   for(int j = 0; j < total; j++)
   {
      MqlCalendarEvent evento;
      if(!CalendarEventById(valores[j].event_id, evento))
         continue;

      bool es_match;
      if(usar_filtro_cpi)
         es_match = (StringFind(evento.name, "Consumer Price Index") >= 0 ||
                     StringFind(evento.name, "CPI") >= 0);
      else
         es_match = (StringFind(evento.name, "Fed") >= 0 ||
                     StringFind(evento.name, "Interest Rate") >= 0 ||
                     StringFind(evento.name, "FOMC") >= 0);

      if(!es_match)
         continue;

      encontro = true;
      total_encontrados_global++;

      int digits = (int)evento.digits;
      double factor = MathPow(10, digits);

      MqlCalendarCountry pais;
      string country_str = "N/A";
      if(CalendarCountryById(evento.country_id, pais))
         country_str = pais.code;

      FileWrite(handle_global,
         TimeToString(objetivo, TIME_DATE),
         etiqueta_categoria,
         TimeToString(valores[j].time, TIME_DATE | TIME_MINUTES),
         evento.name,
         country_str,
         (string)valores[j].actual_value,
         (string)valores[j].forecast_value,
         (string)valores[j].prev_value,
         (string)digits,
         DoubleToString(valores[j].actual_value / factor, digits),
         DoubleToString(valores[j].forecast_value / factor, digits)
      );
   }

   if(!encontro)
   {
      Print("Ventana ", TimeToString(objetivo, TIME_DATE), " (", etiqueta_categoria, "): ",
            total, " eventos US pero ninguno matcheo el filtro -- candidatos reales:");
      for(int j = 0; j < total; j++)
      {
         MqlCalendarEvent ev;
         if(CalendarEventById(valores[j].event_id, ev))
            Print("  -> ", ev.name, " | ", TimeToString(valores[j].time, TIME_DATE | TIME_MINUTES));
      }
      FileWrite(handle_global, TimeToString(objetivo, TIME_DATE), etiqueta_categoria,
                "SIN_MATCH_NOMBRE", "", "", "", "", "", "", "");
   }
}

void OnStart()
{
   handle_global = FileOpen("macro_calendar_check.csv", FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ',');
   if(handle_global == INVALID_HANDLE)
   {
      Print("ERROR: no se pudo crear el archivo CSV. Codigo: ", GetLastError());
      return;
   }

   FileWrite(handle_global, "fecha_objetivo", "categoria", "event_time", "event_name", "country",
             "actual_value_raw", "forecast_value_raw", "prev_value_raw",
             "digits", "actual_escalado", "forecast_escalado");

   for(int i = 0; i < ArraySize(fechas_cpi); i++)
      ProcesarVentana(fechas_cpi[i], "CPI", true);

   for(int i = 0; i < ArraySize(fechas_fomc); i++)
      ProcesarVentana(fechas_fomc[i], "FOMC", false);

   FileClose(handle_global);
   Print("Eventos encontrados (CPI+FOMC): ", total_encontrados_global, "/6");
   Print("CSV: C:\\Users\\josem\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\macro_calendar_check.csv");
}
