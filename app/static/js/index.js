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
  <a class='btn btn-light' v-on:click="stop_wtc" v-if="wtc.switch">Stop</a>
  <a class='btn btn-light' v-on:click="start_wtc" v-else>Start</a>

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
  <button class="btn btn-light" v-on:click="onSubmitUpdate">Update</button>
  <button class="btn btn-light" v-on:click="onResetUpdate">Cancel</b-button>
  </b-button-group>

  <b-button  class="btn btn-danger float-right" v-on:click="onRemove">Remove</b-button>
  </b-form>
  </b-modal>
  </tr>
  `,
  mounted: function () {
    this.log_url = '/details_wtc/' + this.wtc.id;
  },

  methods: {
    get_wtc: function () {
      const path = '/wtc/' + this.wtc.id;
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
      if (!this.wtc.switch){
        clearInterval(this.timer);
        console.log('Closed it');
      }
      if (this.wtc.switch && !this.timer) {
        this.timer = setInterval(this.get_wtc, this.wtc.sleeptime*1000);
      }
    },
    edit_wtc: function () {
      this.editForm = this.wtc;
      this.showEditModal = !this.showEditModal;
    },
    start_wtc: function () {
      this.timer = setInterval(this.get_wtc, this.wtc.sleeptime*1000);
      const path = '/start/wtc/' + this.wtc.id;
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    },
    stop_wtc: function () {
      clearInterval(this.timer);
      const path = '/stop/wtc/' + this.wtc.id;
      axios.get(path)
      .then((res) => {
        this.wtc = res.data.wtc;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
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
    onRemove: function() {
      const path = '/wtc/' + this.wtc.id;
      axios.delete(path)
      .then(() => {
      this.$emit('refresh');
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
        this.$emit('refresh');
      });
    },
  },

  created: function () {
    if  (this.wtc.switch) {
      this.timer = setInterval(this.get_wtc, this.wtc.sleeptime*1000);
    }
  },
  beforeDestroy () {
    clearInterval(this.timer)
  }
});

Vue.component('wtc-table', {
  template: `
  <span>
  <a class='btn btn-light' v-on:click="add_wtc">Add WebTempControl</a>
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
  <wtc-widget v-for="wtc in wtcs" v-bind:wtc="wtc" :key="wtc.index" @refresh="get_wtcs"/>
  </tbody>
  </table>


  <b-modal title="Add" hide-footer v-model="showAddModal">
  <b-form class="form-horizontal">
  <b-form-group id="form-name-edit-group" label="Name:" label-for="form-name-edit-input">
  <b-form-input id="form-name-edit-input" type="text"
  v-model="addForm.name" required placeholder="Enter name">
  </b-form-input>
  <b-form-group id="form-ip-edit-group" label="IP Adress:" label-for="form-ip-edit-input">
  <b-form-input id="form-ip-edit-input" type="text"
  v-model="addForm.ip_adress" required placeholder="Enter adress">
  </b-form-input>
  <b-form-group id="form-port-edit-group" label="Port:" label-for="form-port-edit-input">
  <b-form-input id="form-port-edit-input" type="text"
  v-model="addForm.port" required placeholder="Enter port">
  </b-form-input>

  </b-form-group>
  <b-button-group>
  <button type="button" variant="btn btn-light" v-on:click="onSubmitAdd">Update</button>
  <b-button type="reset" variant="danger" v-on:click="onResetAdd">Cancel</b-button>
  </b-button-group>
  </b-form>
  </b-modal>
  </tr>
  </span>
  `,
  data: function () {
    return {
      wtcs: [],
      showAddModal: false,
      addForm: []
    }
  },
  methods: {
    get_wtcs: function () {
      const path = '/wtc/';
      axios.get(path)
      .then((res) => {
        this.wtcs = res.data.wtcs;
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    },
    add_wtc: function () {
      this.showAddModal = true;
    },
    onSubmitAdd: function () {
      this.showAddModal = !this.showAddModal;
      const payload = {
        name: this.addForm.name,
        ip_adress: this.addForm.ip_adress,
        port: this.addForm.port
      };
      const path = '/wtc/';
      axios.post(path, payload)
      .then(() => {
        this.get_wtcs();
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
        this.get_wtcs();
      });
    },
    onResetAdd: function () {
      this.addForm = [];
      this.showAddModal = !this.showAddModal;
    },

  },
  mounted: function () {
    this.get_wtcs();
  },
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
