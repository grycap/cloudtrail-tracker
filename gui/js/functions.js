
function print(x){
    console.log(x)
}

function select(value){
    $("#function").html(value)
    user_name = $(".user_name")
    time1 = $(".time1")
    time2 = $(".time2")
    event_name = $(".event_name")
    used_services_parameter = $(".used_services_parameter")
    used_services_parameter_value = $(".used_services_parameter_value")
    count = $(".checkbox")

    switch (value) {
        case 'users_list':
            user_name.hide()
            time1.hide()
            time2.hide()
            event_name.hide()
            used_services_parameter.hide()
            used_services_parameter_value.hide()
            count.hide()
            break;

        case 'actions_between':
            user_name.hide()
            time1.show()
            time2.show()
            event_name.show()
            used_services_parameter.show()
            used_services_parameter_value.show()
            count.show()
            break;

        case 'used_services':
            user_name.show()
            time1.show()
            time2.show()
            event_name.hide()
            used_services_parameter.hide()
            used_services_parameter_value.hide()
            count.show()
            break;

        case 'used_services_parameter':
            user_name.show()
            time1.show()
            time2.show()
            event_name.hide()
            used_services_parameter.show()
            used_services_parameter_value.show()
            count.show()
            break;

        case 'user_count_event':
            user_name.show()
            time1.show()
            time2.show()
            event_name.show()
            used_services_parameter.show()
            used_services_parameter_value.show()
            count.show()
            break;

        case 'top_users':
            user_name.hide()
            time1.show()
            time2.show()
            event_name.show()
            used_services_parameter.show()
            used_services_parameter_value.show()
            count.hide()
            break;

    }


}