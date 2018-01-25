// API_url = "https://aekot17gqj.execute-api.us-east-1.amazonaws.com/test/alucloud230query"
// API_url = " https://ucxi51mw43.execute-api.us-east-1.amazonaws.com/QueryStage230/alucloud230Query/{type}/{event}/{user}/{count}/{time1}/{time2}"
API_url = " https://ucxi51mw43.execute-api.us-east-1.amazonaws.com/QueryStage230/alucloud230Query/"
datos = null

function print(x) {
    console.log(x)
}

function count_events_day(data) {
    counter = {}

    for (var d in data) {
        elem = data[d]
        key = String(elem.eventTime).substring(0, 10)
        count = counter[key]
        if (!count) {
            counter[key] = 1
        } else {
            counter[key] = count + 1
        }

    }

    list = []

    for (var key in counter) {

        list.push([key, counter[key]])
    }
    list.sort(function (a, b) {

        a = new Date(a[0]);
        b = new Date(b[0]);
        return a < b ? -1 : a > b ? 1 : 0;
    });
    return list
}

function count_per_event(data) {
     counter = {}
    for (var d in data) {
        elem = data[d]
        key = String(elem.eventSource).split(".")[0]
        // print(key)
        count = counter[key]
        if (!count) {
            counter[key] = 1
        } else {
            counter[key] = count + 1
        }

    }

    list = []

    for (var key in counter) {

        list.push([key, counter[key]])
    }

    return list
}

function graph(data) {
    datos = data
    // set the dimensions and margins of the graph
    var margin = {top: 20, right: 20, bottom: 100, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

// parse the date / time
// var parseTime = d3.timeParse("%d-%b-%y"); // 25-Apr-12
    var parseTime = d3.timeParse("%Y-%m-%d"); // 2017-10-31

// set the ranges
    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

// define the line
    var valueline = d3.line()
        .x(function (d) {
            return x(d.date);
        })
        .y(function (d) {
            return y(d.number);
        });

// append the svg obgect to the body of the page
// appends a 'group' element to 'svg'
// moves the 'group' element to the top left margin
    $("#events").empty()
    var svg = d3.select("#events").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

// Get the data
// d3.csv("data.csv", function(error, data) {
//     d3.csv("event_days.csv", function (error, data) {
//         if (error) throw error;
    data = JSON.parse(data)
    data = count_events_day(data)
    // format the data
    data.forEach(function (d) {
        // print(d)
        d.date = parseTime(d[0]);
        d.number = +d[1];
    });

    // Scale the range of the data
    x.domain(d3.extent(data, function (d) {
        return d.date;
    }));
    y.domain([0, d3.max(data, function (d) {
        return d.number;
    })]);

    // Add the valueline path.
    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline);

    // Add the X Axis
    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x)
            .tickFormat(d3.timeFormat("%Y-%m-%d")))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

    // Add the Y Axis
    svg.append("g")
        .attr("class", "axis")
        .call(d3.axisLeft(y));

    // });

}

function bars(data) {
    // print(data)
    data = JSON.parse(data)
    data = count_per_event(data);
    print(data)
    $("#events").empty()
        var margin = {top: 20, right: 20, bottom: 100, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;
    var svg = d3.select("#events").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.scaleBand().rangeRound([0, width]).padding(0.1),
        y = d3.scaleLinear().rangeRound([height, 0]);

    var g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

     data.forEach(function (d) {
        // print(d)
        d.letter = d[0];
        d.frequency = +d[1];
    });


    x.domain(data.map(function (d) {
        return d.letter;
    }));
    y.domain([0, d3.max(data, function (d) {
        return d.frequency;
    })]);

    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    g.append("g")
        .attr("class", "axis axis--y")
        .call(d3.axisLeft(y).ticks(10, ""))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("Frequency");

    var bar = g.selectAll(".bar")
        .data(data)
        .enter()
        .append("g")

    bar.append("rect")
        .attr("class", "bar")
        .attr("x", function (d) {
            return x(d.letter);
        })
        .attr("y", function (d) {
            return y(d.frequency);
        })
        .attr("width", x.bandwidth())
        .attr("height", function (d) {
            return (height - y(d.frequency)) * 1;
        })
        .attr("fill", function (d) {
            return "rgb(0, 0, " + (d.frequency * 10) + ")";
        })


    barHeight = 20
    bar.append("text")
        .attr("x", function (d) {
            return x(d.letter) + 25;
        })
        .attr("y", function (d) {
            return y(d.frequency) - 10
        })
        .attr("dy", ".35em")
        .text(function (d) {
            return d.frequency;
        });




}

parameters = {
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

//date = YYYY-MM-DD
function timeFormat(date) {
    date = date + "T00:00:00Z"
    return date
}

function scan() {

    type = $("#function").val()
    user_name = $("#user_name").val()
    time1 = $("#time1").val()
    time2 = $("#time2").val()
    event_name = $("#event_name").val()
    used_services_parameter = $("#used_services_parameter").val()
    used_services_parameter_value = $("#used_services_parameter_value").val()
    count = $("#checkbox").is(":checked")

    parameters["type"] = type
    parameters["count"] = count
    parameters["user"] = user_name
    parameters["time1"] = time1
    parameters["time2"] = time2
    parameters["event"] = event_name
    parameters["request_parameter"] = [
        used_services_parameter, used_services_parameter_value
    ]
    time1 = timeFormat(time1)
    time2 = timeFormat(time2)
    print(parameters)
    //{type}/{event}/{user}/{count}/{time1}/{time2}
    url = API_url + type + "/" + event_name + "/" + user_name + "/" + count + "/" +time1 + "/" + time2
    print(url)
    jQuery.ajax({
        url: API_url,
        // type: 'GET',
        contentType: "application/json",
        // data: JSON.stringify(parameters),
        success: function (data) {
            console.log("Success")
            // print(data)
            by_event = $("#by_event").is(":checked")
            if (by_event) {
                bars(data)
            } else
                graph(data)

        },
        error: function (jqXHR, textStatus, errorThrown) {
            var code = jqXHR.status

            console.log(("error " + code));
            console.log(jqXHR.responseText)
            console.log(jqXHR)

        },
    })
}
