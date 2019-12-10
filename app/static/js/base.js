Vue.component('wtc-widget', {
  props: ['wtc'],
  data: function () {
    return {
      settings_url: '',
      log_url: '',
      start_url: '',
      stop_url: '',
      value:'Empty',
      timer: '',
      showEditModal: false,
      editForm: []
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
  <button type="button" class="btn btn-light" v-on:click="edit_wtc">Settings</button>
  <a class='btn btn-light' target="_blank" :href="log_url">Log</a>
  <a class='btn btn-light' :href="stop_url" v-if="wtc.switch">Stop</a>
  <a class='btn btn-light' :href="start_url" v-else>Start</a>
  <td>

  <b-modal title="Update" hide-footer v-model="showEditModal">
  <b-form class="form-horizontal">
  <b-form-group id="form-name-edit-group" label="Name:" label-for="form-name-edit-input">
  <b-form-input id="form-name-edit-input" type="text"
  v-model="editForm.name" required placeholder="Enter name">
  </b-form-input>
  <b-form-group id="form-ip-edit-group" label="IP Adress:" label-for="form-ip-edit-input">
  <b-form-input id="form-ip-edit-input" type="text"
  v-model="editForm.ip_adress" required placeholder="Enter adress">
  </b-form-input>
  <b-form-group id="form-port-edit-group" label="Port:" label-for="form-port-edit-input">
  <b-form-input id="form-port-edit-input" type="text"
  v-model="editForm.port" required placeholder="Enter port">
  </b-form-input>
  <b-form-group id="form-wt-edit-group" label="Wait time:" label-for="form-wt-edit-input">
  <b-form-input id="form-wt-edit-input" type="text"
  v-model="editForm.sleeptime" required placeholder="Enter waittime">
  </b-form-input>
  <b-form-group id="form-setpoint-edit-group" label="Setpoint:" label-for="form-setpoint-edit-input">
  <b-form-input id="form-setpoint-edit-input" type="text"
  v-model="editForm.setpoint" required placeholder="Enter setpoint">
  </b-form-input>
  <b-form-group id="form-gain-edit-group" label="Gain:" label-for="form-gain-edit-input">
  <b-form-input id="form-gain-edit-input" type="text"
  v-model="editForm.gain" required placeholder="Enter gain">
  </b-form-input>
  <b-form-group id="form-integral-edit-group" label="tauI (s):" label-for="form-integral-edit-input">
  <b-form-input id="form-integral-edit-input" type="text"
  v-model="editForm.integral" required placeholder="Enter tauI">
  </b-form-input>
  <b-form-group id="form-diff-edit-group" label="tauD (s):" label-for="form-diff-edit-input">
  <b-form-input id="form-diff-edit-input" type="text"
  v-model="editForm.diff" required placeholder="Enter tauD">
  </b-form-input>

  </b-form-group>
  <b-button-group>
  <button type="button" variant="btn btn-light" v-on:click="onSubmitUpdate">Update</button>
  <b-button type="reset" variant="danger" v-on:click="onResetUpdate">Cancel</b-button>
  </b-button-group>
  </b-form>
  </b-modal>
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
      const path = '/wtc/' + this.wtc.id;
      console.log(path);
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    },

    edit_wtc: function () {
      this.editForm = this.wtc;
      this.showEditModal = !this.showEditModal;
    },
    onSubmitUpdate: function () {
      this.showEditModal = !this.showEditModal;
      const payload = {
        name: this.editForm.name,
        ip_adress: this.editForm.ip_adress,
        port: this.editForm.port,
        sleeptime: this.editForm.sleeptime,
        setpoint: this.editForm.setpoint,
        gain: this.editForm.gain,
        integral: this.editForm.integral,
        diff: this.editForm.diff
      };
      console.log(payload)
      const path = '/wtc/' + this.wtc.id;
      axios.put(path, payload)
        .then(() => {
        this.get_wtc();
      })
      .catch((error) => {
      // eslint-disable-next-line
      console.error(error);
      this.get_wtc();
    });
    },
    onResetUpdate: function () {
      this.editForm = this.wtc;
      this.showEditModal = !this.showEditModal;
    },
  },

  created: function () {
      this.timer = setInterval(this.get_wtc, this.wtc.sleeptime*1000)
    },
    beforeDestroy () {
      clearInterval(this.timer)
    }
  });

Vue.component('wtc-summary-table', {
  props: ['id'],
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
  <wtc-widget v-bind:wtc="wtc"/>
  </tbody>
  </table>
  `,
  data: function () {
    return {
      wtc: []
    }
  },
  methods: {
    get_wtc: function () {
      const path = '/wtc/' + this.id;
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    }
  },
  mounted: function () {
    this.get_wtc();
  }
});

var IndexVue = new Vue({
  el: '#wtcTable'
});


Vue.component('wtc-widget', {
  props: ['wtc'],
  data: function () {
    return {
      settings_url: '',
      log_url: '',
      start_url: '',
      stop_url: '',
      value:'Empty',
      timer: '',
      showEditModal: false,
      editForm: []
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
  <button type="button" class="btn btn-light" v-on:click="edit_wtc">Settings</button>
  <a class='btn btn-light' target="_blank" :href="log_url">Log</a>
  <a class='btn btn-light' :href="stop_url" v-if="wtc.switch">Stop</a>
  <a class='btn btn-light' :href="start_url" v-else>Start</a>
  <td>

  <b-modal title="Update" hide-footer v-model="showEditModal">
  <b-form class="form-horizontal">
  <b-form-group id="form-name-edit-group" label="Name:" label-for="form-name-edit-input">
  <b-form-input id="form-name-edit-input" type="text"
  v-model="editForm.name" required placeholder="Enter name">
  </b-form-input>
  <b-form-group id="form-ip-edit-group" label="IP Adress:" label-for="form-ip-edit-input">
  <b-form-input id="form-ip-edit-input" type="text"
  v-model="editForm.ip_adress" required placeholder="Enter adress">
  </b-form-input>
  <b-form-group id="form-port-edit-group" label="Port:" label-for="form-port-edit-input">
  <b-form-input id="form-port-edit-input" type="text"
  v-model="editForm.port" required placeholder="Enter port">
  </b-form-input>
  <b-form-group id="form-wt-edit-group" label="Wait time:" label-for="form-wt-edit-input">
  <b-form-input id="form-wt-edit-input" type="text"
  v-model="editForm.sleeptime" required placeholder="Enter waittime">
  </b-form-input>
  <b-form-group id="form-setpoint-edit-group" label="Setpoint:" label-for="form-setpoint-edit-input">
  <b-form-input id="form-setpoint-edit-input" type="text"
  v-model="editForm.setpoint" required placeholder="Enter setpoint">
  </b-form-input>
  <b-form-group id="form-gain-edit-group" label="Gain:" label-for="form-gain-edit-input">
  <b-form-input id="form-gain-edit-input" type="text"
  v-model="editForm.gain" required placeholder="Enter gain">
  </b-form-input>
  <b-form-group id="form-integral-edit-group" label="tauI (s):" label-for="form-integral-edit-input">
  <b-form-input id="form-integral-edit-input" type="text"
  v-model="editForm.integral" required placeholder="Enter tauI">
  </b-form-input>
  <b-form-group id="form-diff-edit-group" label="tauD (s):" label-for="form-diff-edit-input">
  <b-form-input id="form-diff-edit-input" type="text"
  v-model="editForm.diff" required placeholder="Enter tauD">
  </b-form-input>

  </b-form-group>
  <b-button-group>
  <button type="button" variant="btn btn-light" v-on:click="onSubmitUpdate">Update</button>
  <b-button type="reset" variant="danger" v-on:click="onResetUpdate">Cancel</b-button>
  </b-button-group>
  </b-form>
  </b-modal>
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
      const path = '/wtc/' + this.wtc.id;
      console.log(path);
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    },

    edit_wtc: function () {
      this.editForm = this.wtc;
      this.showEditModal = !this.showEditModal;
    },
    onSubmitUpdate: function () {
      this.showEditModal = !this.showEditModal;
      const payload = {
        name: this.editForm.name,
        ip_adress: this.editForm.ip_adress,
        port: this.editForm.port,
        sleeptime: this.editForm.sleeptime,
        setpoint: this.editForm.setpoint,
        gain: this.editForm.gain,
        integral: this.editForm.integral,
        diff: this.editForm.diff
      };
      console.log(payload)
      const path = '/wtc/' + this.wtc.id;
      axios.put(path, payload)
        .then(() => {
        this.get_wtc();
      })
      .catch((error) => {
      // eslint-disable-next-line
      console.error(error);
      this.get_wtc();
    });
    },
    onResetUpdate: function () {
      this.editForm = this.wtc;
      this.showEditModal = !this.showEditModal;
    },
  },

  created: function () {
      this.timer = setInterval(this.get_wtc, this.wtc.sleeptime*1000)
    },
    beforeDestroy () {
      clearInterval(this.timer)
    }
  });

Vue.component('wtc-props', {
  props: ['wtc'],
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
  <wtc-widget v-bind:wtc="wtc"/>
  </tbody>
  </table>
  `,
  data: function () {
    return {
      wtc: []
    }
  },
  methods: {
    get_wtc: function () {
      const path = '/wtc/' + this.id;
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    }
  },
  mounted: function () {
    this.get_wtc();
  }
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

  socket.on('close_conn', function(msg) {
    var el_name = '#' + msg.data;
    console.log(el_name)
    $(el_name).html('Closed');
    $(el_name).attr("class","bg-warning")
  });

  socket.on('open_conn', function(msg) {
    var el_name = '#' + msg.data;
    console.log(el_name)
    $(el_name).html('Open');
    $(el_name).attr("class","bg-success")
  });

  // Event handler for server sent data.
  socket.on('my_response', function(msg) {
    $('#log').prepend('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
  });

  socket.on('wlog_response', function(msg) {
    console.log('new stuff');
    var count = msg.count;
    var data = msg.data;
    var time = msg.time;
    var id = msg.id;
    var this_id =  '{{ ard.id }}';
    console.log(id);
    console.log(this_id);
    if (id == this_id){
      if (data.length == 4 && data[3] == 0) {
        var ard_log_str = '<tr class="warning">';
      }
      else {
        var ard_log_str = '<tr>';
      }
      ard_log_str = ard_log_str + '<th scope="row">' + msg.count +'</th>';
      ard_log_str = ard_log_str + '<td>' + msg.time +'</td>';
      for (var i=0; i<data.length; i++){

        ard_log_str = ard_log_str + '<td>' + data[i] +'</td>';
      }
      ard_log_str = ard_log_str + '</tr>'

      $('#ard_log > tbody').prepend(ard_log_str).html()

      Plotly.extendTraces('plot', {
        x:[[time], [time], [time]],
        y:[[data[0]], [data[1]], [data[3]]]
      }, [0,1,2])
    }
  });

  function download_csv(csv, filename) {
    var csvFile;
    var downloadLink;

    // CSV FILE
    csvFile = new Blob([csv], {type: "text/csv"});

    // Download link
    downloadLink = document.createElement("a");

    // File name
    downloadLink.download = filename;

    // We have to create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);

    // Make sure that the link is not displayed
    downloadLink.style.display = "none";

    // Add the link to your DOM
    document.body.appendChild(downloadLink);

    // Lanzamos
    downloadLink.click();
  }

  function export_table_to_csv(html, filename) {
    var csv = [];
    var rows = document.querySelectorAll("table tr");
    var rows = $("#ard_log tr");

    for (var i = 0; i < rows.length; i++) {
      var row = [], cols = rows[i].querySelectorAll("td, th");

      for (var j = 0; j < cols.length; j++)
      row.push(cols[j].innerText);

      csv.push(row.join(","));
    }

    // Download CSV
    download_csv(csv.join("\n"), filename);
  }
  $( "#exp_button" ).click(function() {
    var html = $("#ard_log").outerHTML;
    export_table_to_csv(html, "table.csv");
  });

  // set up the plotting
  var setpoint_trace = {
    x: [],
    y: [],
    name: 'Setpoint',
    type: 'scatter'
  };

  var input_trace = {
    x: [],
    y: [],
    name: 'Measured T',
    type: 'scatter'
  };

  var control_trace = {
    x: [],
    y: [],
    name: 'Control',
    type: 'scatter',
    yaxis: 'y2'
  };

  var data = [ setpoint_trace, input_trace, control_trace];
  var layout = {
    yaxis2: {
      title: 'Control',
      overlaying: 'y',
      side: 'right',
      tickfont: {color: '#2ca02c'},
      titlefont: {color: '#2ca02c'},
    }};

    Plotly.newPlot('plot', data, layout);
  });
