from django import template

register = template.Library()

def customer_submit_row(context):
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    
    show_cancel = True
    is_gen_api_key = False

    if(context.has_key('show_cancel')):
        show_cancel = context['show_cancel']

    if(context.has_key('is_gen_api_key')):
        is_gen_api_key = context['is_gen_api_key']

    return {
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and
                            not is_popup and (not save_as or context['add']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'show_cancel':show_cancel,
        'is_gen_api_key': is_gen_api_key,
    }

customer_submit_row = register.inclusion_tag('admin/control_panel/submit_line.html', takes_context=True)(customer_submit_row)
