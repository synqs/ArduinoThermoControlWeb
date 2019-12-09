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
        console.log(this.wtc);
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
      <wtc-widget v-for="wtc in wtcs" v-bind:wtc="wtc"/>
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
          console.log('Get the wtcs');
          const path = '/read_wtcs/';
          axios.get(path)
            .then((res) => {
              console.log(res.data);
            this.wtcs = res.data.wtcs;
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });
          console.log(this.wtcs);
        }
    },
      mounted: function () {
        this.get_wtcs();

      }
  });

var IndexVue = new Vue({
    el: '#wtcTable'
  });

$(document).ready(function() {
  namespace = '';
  // Connect to the Socket.IO server.
  // The connection URL has the following format:
  //     http[s]://<domain>:<port>[/<namespace>]
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
  // Event handler for new connections.
  socket.on('connect', function() {
    socket.emit('my_response', {data: 'I\'m connected!'});
  });

  // Event handler for server sent data.
  socket.on('my_response', function(msg) {
    $('#log').prepend('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
  });

  socket.on('close_conn', function(msg) {
    var el_name = '#' + msg.data;
    $(el_name).html('Closed');
    $(el_name).attr("class","bg-warning")
  });

  socket.on('open_conn', function(msg) {
    var el_name = '#' + msg.data;
    var button_name = '#' + msg.data;
    $(el_name).html('Open');
    $(el_name).attr("class","bg-success")
  });

  socket.on('wtemp_value', function(msg) {
    var temp = msg.data;
    var id = msg.id;
    var el_name = '#read_wtc' + msg.id;
    $(el_name).html(temp);
  });

  socket.on('temp_value', function(msg) {
    var temp = msg.data;
    var id = msg.id;
    var el_name = '#read_tc' + msg.id;
    $(el_name).html(temp);
  });

  socket.on('serial_value', function(msg) {
    var temp = msg.data;
    var id = msg.id;
    var el_name = '#read_sm' + msg.id;
    $(el_name).html(temp);
  });

  socket.on('camera_response', function(msg) {
    var Natoms = msg.Nat;
    var id = msg.id;
    var el_name = '#read_camera' + id;
    $(el_name).html(Natoms);
  });

  // Interval function that tests message latency by sending a "ping"
  var ping_pong_times = [];
  var start_time;
  window.setInterval(function() {
    start_time = (new Date).getTime();
    socket.emit('my_ping');
  }, 1000);

  socket.on('my_pong', function() {
    var latency = (new Date).getTime() - start_time;
    ping_pong_times.push(latency);
    ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
    var sum = 0;
    for (var i = 0; i < ping_pong_times.length; i++)
    sum += ping_pong_times[i];
    $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
  });
});
