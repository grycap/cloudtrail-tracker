
function print(x){
    console.log(x)
}

function select(value){
    $("#function").html(value)
    $("#function").val(value)
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
            $("#used_services_parameter_kinput").val("")
            $("#used_services_parameter_vinput").val("")
            used_services_parameter_value.hide()
            count.hide()
            break;

        case 'actions_between':
            $("#function").html("Acciones entre dos fechas")
            user_name.hide()
            time1.show()
            time2.show()
            event_name.show()
            used_services_parameter.show()
            used_services_parameter_value.show()
            count.show()
            break;

        case 'used_services':
            $("#function").html("Servicios usados")
            user_name.show()
            time1.show()
            time2.show()
            event_name.hide()
            used_services_parameter.hide()
            used_services_parameter_value.hide()
            $("#used_services_parameter_kinput").val("")
            $("#used_services_parameter_vinput").val("")
            count.show()
            break;

        case 'used_services_parameter':
            $("#function").html("Servicios usados con filtro")
            user_name.show()
            time1.show()
            time2.show()
            event_name.hide()
            used_services_parameter.show()
            used_services_parameter_value.show()
            count.show()
            break;

        case 'user_count_event':
            $("#function").html("Contador de eventos")
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

function cognito(){
    var data = { UserPoolId : 'us-east-1_31YsM4yXE',
        ClientId : 'ab7b29ef-b16e-41c1-b854-5e29b3c10315'
    };
    var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(data);
    var cognitoUser = userPool.getCurrentUser();

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            console.log('session validity: ' + session.isValid());
        });
    }

}