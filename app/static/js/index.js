Vue.component('wtc-widget', {
  props: ['wtc'],
  data: function () {
    return {
      settings_url: '',
      log_url: '',
      start_url: '',
      stop_url: '',
      value:'Empty',
      timer: ''
    }
  },
  template: `
  <tr>
  <td> {{ wtc.id }} </td>
  <td>{{ wtc.name }}</td>
  <td class="bg-success" v-if="wtc.switch">Open</td>
  <td class="bg-warning" v-else>Closed</td>
  <td>{{ wtc.setpoint }}</td>
  <td > {{ wtc.value }}</td>
  <td>
  <a class='btn btn-light' target="_blank" :href="settings_url">Settings</a>
  <a class='btn btn-light' target="_blank" :href="log_url">Log</a>
  <a class='btn btn-light' :href="stop_url" v-if="wtc.switch">Stop</a>
  <a class='btn btn-light' :href="start_url" v-else>Start</a>
  <td>
  </tr>
  `,
  mounted: function () {
    this.settings_url = '/change_wtc/' + this.wtc.id;
    this.log_url = '/details_wtc/' + this.wtc.id;
    this.start_url = '/start_wtc/' + this.wtc.id;
    this.stop_url = '/stop_wtc/' + this.wtc.id;

  },
  methods: {
    get_wtc: function () {
      console.log('Get the wtc');
      const path = '/read_wtc/' + this.wtc.id;
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    }
  }
  , created: function () {
    this.timer = setInterval(this.get_wtc, this.wtc.sleeptime*1000)
  },
  beforeDestroy () {
    clearInterval(this.timer)
  }
});

Vue.component('wtc-table', {
  props: ['wtcs_str'],
  template: `
  <table class="table table-hover">
  <thead>
  <tr>
  <th scope="col">#</th>
  <th scope="col">Name</th>
  <th scope="col">Status</th>
  <th scope="col">Setpoint</th>
  <th scope="col">Current Value</th>
  <th scope="col">Other actions </th>
  </tr>
  </thead>
  <tbody>
  <wtc-widget v-for="wtc in wtcs" v-bind:wtc="wtc" :key="wtc.index"/>
  </tbody>
  </table>
  `,
  data: function () {
    return {
      wtcs: []
    }
  },
  methods: {
    get_wtcs: function () {
      const path = '/read_wtcs/';
      axios.get(path)
      .then((res) => {
        this.wtcs = res.data.wtcs;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    }
  },
  mounted: function () {
    this.get_wtcs();

  }
});

var IndexVue = new Vue({
  el: '#wtcTable'
});



Vue.component('ping-pong-widget', {
  data: function () {
    return {
      ping_pong_times: [],
      time: '',
      timer: ''
    }
  },
  template: `
  <p>Average ping/pong latency: <b>{{ time }}  ms</b></p>
  <tr>
  `,
  methods: {
    ping_pong: function () {
      var start_time = (new Date).getTime();
      const path = '/';
      axios.get(path);
      var latency = (new Date).getTime() - start_time;
      this.ping_pong_times.push(latency);
      this.ping_pong_times = this.ping_pong_times.slice(-30); // keep last 30 samples
      var sum = 0;
      for (var i = 0; i < this.ping_pong_times.length; i++)
      sum += this.ping_pong_times[i];

      this.time = Math.round(10 * sum / this.ping_pong_times.length) / 10;
    }
  }
  , created: function () {
    this.timer = setInterval(this.ping_pong, 1000)
  },
  beforeDestroy () {
    clearInterval(this.timer)
  }
});

var PingPongVue = new Vue({
  el: '#ping-pong-test'
});
