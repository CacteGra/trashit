import json

from django.db.utils import DataError

from datapop.models import RegisterAPI, RegisterAPIChosen, Chosen

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

def spec_polygon(using_dict):
    for list_id, i in enumerate(using_dict):
        if '[][][]' in i:
            del using_dict[list_id]
            del using_dict[list_id-1]
            using_dict[list_id-2] = i[:-6]
            break
    return using_dict

def only_one_item(using_dict, l, pk, hierarchy_level, parent):
    api = RegisterAPI.objects.get(pk=pk)
    list_dict = []
    using_dict = [root for root in using_dict if root != '$.']
    using_dict = [root for root in using_dict if root != '$']
    has_list = {'in list': False, 'name': ''}
    has_dict = {'dict_done': False, 'name': ''}
    dict_level = l
    dict_numbered = hierarchy_level
    dict_numbered = hierarchy_level * 10 + 1
    using_dict = spec_polygon(using_dict)
    for i in using_dict:
        follow_list_dict = {'id': dict_numbered }
        if '[]' in i:
            i = i.replace('[]','[0]')
        elif (has_list['in list'] and has_list['name'] and has_list['name'] in i) or (has_dict['dict_done'] and has_dict['name'] and has_dict['name'] in i):
            continue
        else:
            path_list = i.split('.')
            k = path_list[-1]
            has_list = {'in list': False, 'name': ''}
            has_dict = {'dict_done': False, 'name': ''}
            if '[0]' in k:
                has_list = {'in list': True, 'name': k}
                dict_level = dict_level[k.replace('[0]', '')]
                follow_list_dict['title'] = k.replace('[0]', '')
                chosen = Chosen.objects.create(text_chosen=k[:200])
                child = RegisterAPIChosen.objects.create(register_api_foreign=api, the_chosen=chosen, hierarchy=dict_numbered, children_of=parent, is_list=True )
                follow_list_dict['children'] = only_one_item(sorted(hierarchy(dict_level[0])), dict_level[0], k, dict_numbered, child)
            elif isinstance(dict_level[k], dict):
                has_dict = {'dict_done': True, 'name': k}
                follow_list_dict['title'] = k
                try:
                    chosen = Chosen.objects.create(text_chosen=k[:200], value_example=str(dict_level[k])[:200])
                except DataError:
                    chosen = Chosen.objects.create(text_chosen=k[:200], value_example="data")
                child = RegisterAPIChosen.objects.create(register_api_foreign=api, the_chosen=chosen, hierarchy=dict_numbered, children_of=parent)
                follow_list_dict['children'] = only_one_item(sorted(hierarchy(dict_level[k])), dict_level[k], pk, dict_numbered, child)
            else:
                follow_list_dict['title'] = k
                follow_list_dict['value'] = str(dict_level[k])
                chosen = Chosen.objects.create(text_chosen=k[:200], value_example=str(dict_level[k])[:200])
                child = RegisterAPIChosen.objects.create(register_api_foreign=api, the_chosen=chosen, hierarchy=dict_numbered, children_of=parent)
            list_dict.append(follow_list_dict)
            print(list_dict)
            dict_numbered += 1
    return list_dict

def main(l, pk):
    api = RegisterAPI.objects.get(pk=pk)
    one_list_dict = {}
    # Establish data hierarchy
    s = sorted(hierarchy(l))
    using_dict = [root for root in s if root != '$.']
    using_dict = [root for root in s if root != '$']
    has_list = {'in list': False, 'name': ''}
    has_dict = {'dict_done': False, 'name': ''}
    dict_numbered = 1
    one_list_dict['title'] = "root - not displayed"
    one_list_dict['children'] = []
    one_list_dict['id'] = 0
    chosen = Chosen.objects.create(text_chosen="root")
    parent = RegisterAPIChosen.objects.create(register_api_foreign=api, the_chosen=chosen, hierarchy=0, children_of=None)
    # Bypass list when value is polygon (which displays as [][][])
    using_dict = spec_polygon(using_dict)
    for i in using_dict:
        follow_list_dict = {'id': dict_numbered }
        if '[]' in i:
            i = i.replace('[]','[0]')
        if i == '$':
            continue
        elif (has_list['in list'] and has_list['name'] and has_list['name'] in i) or (has_dict['dict_done'] and has_dict['name'] and has_dict['name'] in i):
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
                follow_list_dict['title'] = k.replace('[0]', '')
                chosen = Chosen.objects.create(text_chosen=k[:200])
                child = RegisterAPIChosen.objects.create(register_api_foreign=api, the_chosen=chosen, hierarchy=dict_numbered, children_of=parent, is_list=True)
                follow_list_dict['children'] = only_one_item(sorted(hierarchy(dict_level[0])), dict_level[0], pk, dict_numbered, child)
                print('liste {}'.format(follow_list_dict['children']))
            elif isinstance(dict_level[k], dict):
                has_dict = {'dict_done': True, 'name': k}
                follow_list_dict['title'] = k
                chosen = Chosen.objects.create(text_chosen=k[:200], value_example=str(dict_level[k])[:200])
                child = RegisterAPIChosen.objects.create(register_api_foreign=api, the_chosen=chosen, hierarchy=dict_numbered, children_of=parent)
                follow_list_dict['children'] = only_one_item(sorted(hierarchy(dict_level[k])), dict_level[k], pk, dict_numbered, child)
            else:
                follow_list_dict['title'] = k
                follow_list_dict['value'] = str(dict_level[k])
                chosen = Chosen.objects.create(text_chosen=k[:200], value_example=str(dict_level[k])[:200])
                child = RegisterAPIChosen.objects.create(register_api_foreign=api, the_chosen=chosen, hierarchy=dict_numbered, children_of=parent)
            one_list_dict['children'].append(follow_list_dict)
            dict_numbered += 1
    return one_list_dict

