
var API_url = "https://aekot17gqj.execute-api.us-east-1.amazonaws.com/test/alucloud230query"



function apiCall() {
    var urlvariable;

    urlvariable = "text";

    var ItemJSON;

    ItemJSON = {
      "httpMethod": "POST",
      "type": "used_services",
      "count": "False",
      "user": "amcaar",
      "event": "RunInstances",
      "time1": "2013-06-01T12:00:51Z",
      "time2": "2018-06-01T19:00:51Z",
      "request_parameter": [
        "requestParameters_instanceType",
        "m1.small"
      ]
    }
    $("div").on("click",function(){
          console.log("hii");
          // $.ajax({
          //     dataType:'json',
          //     url: API_url,
          //     type: 'POST',
          //     data: ItemJSON,
          //     success: function(){
          //         alert('hello');
          //     },
          //     error: function() {
          //         alert('error');
          //     }
          // });
        $.post(API_url, ItemJSON, function(data){
            console.log(data);
        });
    });
    }

apiCall()