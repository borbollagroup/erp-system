(function() {
  document.addEventListener('DOMContentLoaded', () => {
    // Ensure elements exist
    const citySel   = document.getElementById('weather-city');
    const dateInp   = document.getElementById('weather-date');
    const tempEl    = document.getElementById('w-temp');
    const condEl    = document.getElementById('w-cond');
    const windEl    = document.getElementById('w-wind');
    const humEl     = document.getElementById('w-hum');
    const hidTemp   = document.getElementById('id_temp_c');
    const hidCond   = document.getElementById('id_condition');
    const hidWind   = document.getElementById('id_wind_kmh');
    const hidHum    = document.getElementById('id_humidity_pct');
    if (!citySel || !dateInp || !tempEl || !condEl || !windEl || !humEl) {
      console.warn('Weather widget: missing elements, aborting');
      return;
    }

    const GS_URL  = 'https://script.google.com/macros/s/.../exec';
    const API_KEY = '6cddd2923580c11024597c9bb7bf5b55';
    const today   = new Date().toISOString().slice(0,10);

    // Initialize date field
    dateInp.value    = dateInp.value || today;
    dateInp.min      = new Date(Date.now()-5*86400000).toISOString().slice(0,10);
    dateInp.max      = new Date(Date.now()+5*86400000).toISOString().slice(0,10);
    dateInp.readOnly = false;

    async function fetchWeather() {
      const city = citySel.value;
      const d    = dateInp.value;
      if (!city || !d) return;
      try {
        let res, data;
        if (d < today) {
          res = await fetch(`${GS_URL}?city=${encodeURIComponent(city)}&date=${d}`);
          const js = await res.json();
          data = js.results && js.results[0];
        } else if (d === today) {
          res = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${API_KEY}&units=metric`);
          data = await res.json();
        } else {
          res = await fetch(`https://api.openweathermap.org/data/2.5/forecast?q=${city}&appid=${API_KEY}&units=metric`);
          const js = await res.json();
          data = js.list.find(i => i.dt_txt.startsWith(d+' 12:00:00')) || js.list[0];
        }
        if (!data) throw new Error('No weather data');

        const t = data.main?.temp ?? data.temp;
        const c = data.weather?.[0].description ?? data.condition;
        const w = data.wind?.speed ?? data.wind;
        const h = data.main?.humidity ?? data.humidity;

        // Update UI
        tempEl.value = t.toFixed(1) + '°C';
        condEl.value = c;
        windEl.value = w;
        humEl.value  = h;

        // Update hidden inputs if present
        if (hidTemp) hidTemp.value = t;
        if (hidCond) hidCond.value = c;
        if (hidWind) hidWind.value = w;
        if (hidHum)  hidHum.value  = h;
      } catch (err) {
        console.error('Weather widget error:', err);
      }
    }

    citySel.addEventListener('change', fetchWeather);
    dateInp.addEventListener('change', fetchWeather);
    fetchWeather();
  });
})();
