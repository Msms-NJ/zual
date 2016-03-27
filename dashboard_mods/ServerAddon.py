
__author__ = 'Ninad Mhatre'

from addonpy.IAddonInfo import IAddonInfo
from jinja2 import Template
import psutil as ps
from datetime import datetime


class ServerAddon(IAddonInfo):
    result = None

    def _get_cpu_stats(self):
        cpu_info = {'processors': ps.cpu_count(), 'times': ps.cpu_times(),
                    'load': ps.cpu_percent(percpu=True)}
        return cpu_info

    def _get_process_stats(self, process):
        p_info = {}
        for p in process:
            p_info[p.pid] = {}
            _p = p_info[p.pid]
            _p['exe'] = p.exe()
            _p['user'] = p.username()
            _p['created_at'] = datetime.fromtimestamp(p.create_time())
            _p['cpu_usage'] = p.cpu_percent()
            _p['memory_usage'] = p.memory_percent()

        return p_info

    def _search(self, name):
        match = []
        for p in ps.process_iter():
            if p.name() == name:
                match.append(p)

        return match

    def _get_memory_stats(self):
        mem_info = {'virtual': {}, 'swap': {}}
        v_mem = ps.virtual_memory()
        s_mem = ps.swap_memory()
    
        _c = mem_info['virtual']
        _c['total'] = v_mem.total
        _c['used'] = v_mem.used
        _c['free'] = v_mem.free
        _c['used_percent'] = v_mem.percent

        _c = mem_info['swap']
        _c['total'] = s_mem.total
        _c['used'] = s_mem.used
        _c['free'] = s_mem.free
        _c['used_percent'] = s_mem.percent

        return mem_info

    def _get_disk_stats(self):
        return ps.disk_usage('/')

    def execute(self, config):
        from collections import OrderedDict
        self.result = OrderedDict()
        self.result['cpu'] = self._get_cpu_stats()
        self.result['memory'] = self._get_memory_stats()
        self.result['disk'] = self._get_disk_stats()
        self.result['process'] = self._get_process_stats(self._search('python'))

    def template(self):
        t = Template('''<div class="col-lg-10"><div class="panel panel-default">
            <div class="panel-heading">
                <h3 class="panel-title"><a data-toggle="collapse" data-parent="#accordion" href="#server">{{ name }}</a></h3>
            </div>
            <div id="server" class="panel-collapse collapse">
                <div class="panel-body">

                    <div class="panel panel-success">
                        <div class="panel-heading">
                            <h3 class="panel-title">CPU Info</h3>
                        </div>
                        <div class="panel-body">
                            <table class="table table-bordered">
                                <tr><td>Processors</td><td>{{ data['cpu']['processors'] }}</td></tr>
                                <tr><td>Server Timings</td><td>{{ data['cpu']['times'].user }}</td></tr>
                                <tr><td>Processors</td><td>{{ data['cpu']['load'] }}%</td></tr>
                            </table>
                        </div>
                    </div>

                    <div class="panel panel-success">
                        <div class="panel-heading">
                            <h3 class="panel-title">Memory Info</h3>
                        </div>
                        <div class="panel-body">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Total</th>
                                        <th>Used</th>
                                        <th>Free</th>
                                        <th>Used %</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for t in data['memory']|sort %}
                                        <tr>
                                            <td>{{ t }}</td>
                                            <td class="bytes">{{ data['memory'][t]['total'] }}</td>
                                            <td class="bytes">{{ data['memory'][t]['used'] }}</td>
                                            <td class="bytes">{{ data['memory'][t]['free'] }}</td>
                                            <td>{{ data['memory'][t]['used_percent'] }}</td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="panel panel-success">
                        <div class="panel-heading">
                            <h3 class="panel-title">Disk Usage of '/'</h3>
                        </div>
                        <div class="panel-body">
                            <table class="table table-bordered">
                                <tr><td>Total</td><td class="bytes">{{ data['disk'].total }}</td></tr>
                                <tr><td>Used (bytes)</td><td class="bytes">{{ data['disk'].used }}</td></tr>
                                <tr><td>Free</td><td class="bytes">{{ data['disk'].free }}</td></tr>
                                <tr><td>Used %</td><td>{{ data['disk'].percent }}</td></tr>
                            </table>
                        </div>
                    </div>

                    <div class="panel panel-success">
                        <div class="panel-heading">
                            <h3 class="panel-title">Process Info</h3>
                        </div>
                        <div class="panel-body">
                            <table class="table table-bordered">
                                <thead>
                                    <th>PID</th>
                                    <th>User</th>
                                    <th>Executable</th>
                                    <th>Created At</th>
                                    <th>CPU Use %</th>
                                    <th>Memory Use %</th>
                                </thead>
                                <tbody>
                                    {% for p in data['process']|sort %}
                                        {% set proc = data['process'][p] %}
                                        <tr>
                                            <td>{{ p }}</td>
                                            <td>{{ proc['user'] }}</td>
                                            <td>{{ proc['exe'] }}</td>
                                            <td>{{ proc['created_at'] }}</td>
                                            <td>{{ proc['cpu_usage'] }}</td>
                                            <td>{{ proc['memory_usage'] }}</td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div></div>''')

        return t.render(data=self.result, name=self.name)

    def get_result(self, as_html=True):
        if as_html:
            return self.template()
        return self.result

    @property
    def name(self):
        return self.__addon__().replace('Addon', ' Info')

    @staticmethod
    def __addon__():
        return 'ServerAddon'