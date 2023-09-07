# response = requests.get("https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Service_WebMercator/MapServer/10/query?where=1%3D1&outFields=*&outSR=4326&f=json")
# d = json.dumps(response.json(), sort_keys=True, indent=4)
# l = json.loads(d)
# h = hierarchy(l)
# s = sorted(h)

def hierarchy(struct, path=None):
    if isinstance(struct, dict):
        path = path if path else '$'
        return set(
            child_path
                for key, obj   in struct.items()
                for child_path in hierarchy(obj, f'{path}.{key}')
        ).union(
            [path]
        )
    elif isinstance(struct, list):
        path = f'{path}[]' if path else '$[]'
        return set(
            child_path
                for obj        in struct
                for child_path in hierarchy(obj, path)
        ).union(
            [path]
        )
    else:
        return [path]

def only_one_item(using_dict, l):
    one_list_dict = {}
    using_dict = [root for root in using_dict if root != '$.']
    using_dict = [root for root in using_dict if root != '$']
    has_list = {'in list': False, 'name': ''}
    has_dict = {'dict_done': False, 'name': ''}
    dict_level = l
    for i in using_dict:
        if '[]' in i:
            i = i.replace('[]','[0]')
        elif (has_list['in list'] and has_list['name'] and has_list['name'] in i) or (has_dict['dict_done'] and has_dict['name'] and has_dict['name'] in i):
            print(has_list['name'])
            print(i)
            continue
        else:
            path_list = i.split('.')
            k = path_list[-1]
            has_list = {'in list': False, 'name': ''}
            has_dict = {'dict_done': False, 'name': ''}
            if '[0]' in k:
                has_list = {'in list': True, 'name': k}
                dict_level = dict_level[k.replace('[0]', '')]
                #print(sorted(hierarchy(dict_level[0])))
                one_list_dict[k.replace('[0]', '')] = only_one_item(sorted(hierarchy(dict_level[0])), dict_level[0])
            elif isinstance(dict_level[k], dict):
                has_dict = {'dict_done': True, 'name': k}
                one_list_dict[k] = only_one_item(sorted(hierarchy(dict_level[k])), dict_level[k])
            else:
                one_list_dict[k] = dict_level[k]
    return one_list_dict

one_list_dict = {}
using_dict = [root for root in s if root != '$.']
using_dict = [root for root in s if root != '$']
has_list = {'in list': False, 'name': ''}
has_dict = {'dict_done': False, 'name': ''}
for i in using_dict:
    if '[]' in i:
        i = i.replace('[]','[0]')
    if i == '$':
        continue
    elif (has_list['in list'] and has_list['name'] and has_list['name'] in i) or (has_dict['dict_done'] and has_dict['name'] and has_dict['name'] in i):
        print(has_list['name'])
        print(i)
        continue
    else:
        path_list = i.split('.')
        dict_level = l
        k = path_list[-1]
        has_list = {'in list': False, 'name': ''}
        has_dict = {'dict_done': False, 'name': ''}
        if '[0]' in k:
            has_list = {'in list': True, 'name': k}
            dict_level = dict_level[k.replace('[0]', '')]
            one_list_dict[k.replace('[0]', ' ')] = [only_one_item(sorted(hierarchy(dict_level[0])), dict_level[0])]
        elif isinstance(dict_level[k], dict):
            has_dict = {'dict_done': True, 'name': k}
            one_list_dict[k] = only_one_item(sorted(hierarchy(dict_level[k])), dict_level[k])
        else:
            dict_level = dict_level[k]
            one_list_dict[k] = dict_level

# print(one_list_dict)


