import re
import os
import glob
import sys
from jinja2 import Template

def parse_sh_nve(filenames):
	r = (".* +(?P<l2vni>\d+) +.* +(?P<mcast>((\d+\.\d+\.\d+\.\d+)|(UnicastBGP))) +.*Up +.*L2 +.*\[(?P<vlan>\d+)\]")
	d = {}
	for filename in filenames:
		with open(filename) as f:
			matches = re.finditer(r, f.read())
			if (matches):
				for match in matches:
					key = match.group('l2vni')
					if key not in d:
						fill = {} 
						d[match.group('l2vni')] = fill
						fill['mcast_group'] = match.group('mcast')
						fill['vlan'] = match.group('vlan')
	return d 


def cfg_list(filenames, regex):
	return [filename for filename in filenames if re.search(regex, filename) is not None]  

def update_dict(*ds):
	res = ds[0].copy()
	for i in range(len(ds)-1):
		res.update(ds[i+1])
	return res

def find_additionals(d1,d2):
	return {k:v for k,v in d2.items() if k not in d1}

def find_intersection(d1,d2):
	return {k:v for k,v in d1.items() if k in d2}

def create_templates():
	vlan_template = """
	{% for vni, data in target.items() -%}
	vlan {{ vni_database[vni].vlan }}
		vn-segment {{ vni }}
	{% endfor -%}
	"""

	evpn_template = """
	evpn
	{% for vni, data in target.items() -%}
		vni {{ vni }} l2
			rd auto
			route-target import {{ asnum }}:{{ vni }}
			route-target export {{ asnum }}:{{ vni }}
	{% endfor -%}
	"""

	nve_template_no_msir = """
	interface nve1
	{% for vni, data in target.items() %}
		member vni {{ vni }}
		{% if 'UnicastBGP' == data.mcast_group -%}
			ingress-replication protocol bgp
		{% else -%}
			mcast_group {{ vni_database[vni].mcast_group }}
		{% endif -%}
	{% endfor %}
	"""

	nve_template_msir = """
	interface nve1
	{% for vni, data in target.items() %}
		member vni {{ vni }}
		multisite ingress-replication
		{% if 'UnicastBGP' == data.mcast_group -%}
			ingress-replication protocol bgp
		{% else -%}
			mcast-group {{ vni_database[vni].mcast_group }}
		{% endif -%}
	{% endfor %}
	"""

	l3vni_associate = """
	interface nve1
	{% for vni, data in target.items() %}
		member vni {{ vni }} associate-vrf
	{% endfor %}
	"""

	j2_vlan_template = Template(vlan_template)
	j2_evpn_template = Template(evpn_template)
	j2_nve_template_no_msir = Template(nve_template_no_msir)
	j2_nve_template_msir = Template(nve_template_msir)
	j2_l3vni_associate = Template(l3vni_associate)

	return {'j2_vlan_template': j2_vlan_template,
			'j2_evpn_template': j2_evpn_template,
			'j2_l3vni_associate': j2_l3vni_associate,
			'j2_nve_template_no_msir': j2_nve_template_no_msir,
			'j2_nve_template_msir': j2_nve_template_msir
			}


def render_pre_works_configs_bg(templates, vni_database, target, asnum):
	return [templates['j2_vlan_template'].render(vni_database=vni_database, target=target),
			templates['j2_evpn_template'].render(asnum=asnum, target=target),
			templates['j2_nve_template_msir'].render(vni_database=vni_database, target=target)]

def render_pre_works_configs_ag_l3vni_associate(templates, vni_database, target, asnum):
	return [templates['j2_l3vni_associate'].render(vni_database=vni_database, target=target)]

def render_pre_works_configs_ag_l2vni_vlan_only(templates, vni_database, target, asnum):
	return [templates['j2_vlan_template'].render(vni_database=vni_database, target=target),
			templates['j2_evpn_template'].render(asnum=asnum, target=target)]

def render_main_works_configs_ag_no_msir(templates, vni_database, target, asnum):
	return [templates['j2_nve_template_no_msir'].render(vni_database=vni_database, target=target)]

def render_main_works_configs_ag_msir(templates, vni_database, target, asnum):
	return [templates['j2_nve_template_msir'].render(vni_database=vni_database, target=target)]

def write_data_to_file(filename, path, data, postfix):
	if os.path.exists(path + "/" + filename + postfix):
		os.remove(path + "/" + filename + postfix)

	with open(path + "/" + filename + postfix, 'a') as f:
		f.write(data)

def main():
	path = sys.argv[1]
	filenames = glob.glob(path + '/*.*')
	site_filenames = cfg_list(filenames, 'SKO-DATA-AC-014.*')
	mpod_filenames = cfg_list(filenames, 'SKO-DATA-BL-.*') + cfg_list(filenames, 'SKO-DATA-AC-MD.*')
	bg_filenames = cfg_list(filenames, 'SKO-DATA-BG-[MD1|MD2].*EXT.*')

	site = parse_sh_nve(site_filenames)
	mpod = parse_sh_nve(mpod_filenames)
	bg = parse_sh_nve(bg_filenames)

	vni_database = update_dict(site, mpod, bg)

	site_mpod = find_intersection(site, mpod)
	site_bg = find_intersection(site, bg)

	ag_bg_add = update_dict(site_mpod, site_bg)
	bg_add = find_additionals(bg,site_mpod)

	templates = create_templates()

	for data in render_pre_works_configs_ag_l2vni_vlan_only(templates, vni_database, ag_bg_add, 65554):
		write_data_to_file('pre-ag', path, data, '-l2vni')

	for data in render_pre_works_configs_bg(templates, vni_database, ag_bg_add, 65554):
		write_data_to_file('pre-bg', path, data, '-all')

	for data in render_pre_works_configs_ag_l3vni_associate(templates, vni_database, ag_bg_add, 65554):
		write_data_to_file('mw1-l3vni-ag-nve-associate', path, data, '-all')

	for data in render_main_works_configs_ag_no_msir(templates, vni_database, ag_bg_add, 65554):
		write_data_to_file('mw1-ag-without-MSIR', path, data, '')

	for data in render_main_works_configs_ag_msir(templates, vni_database, ag_bg_add, 65554):
		write_data_to_file('mw1-ag-with-MSIR', path, data, '')



if __name__ == "__main__":
	main()
