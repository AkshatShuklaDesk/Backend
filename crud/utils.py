def modify_filter(filter_dict):
    final_list = []
    for key,val in filter_dict.items():
        if key == 'search':
            continue
        final_list.append((key,filter_dict['search'],val))
    return final_list