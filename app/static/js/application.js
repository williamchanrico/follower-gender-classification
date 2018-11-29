$(document).ready(function() {
    $('#classify-form').submit(function(e) {
        e.preventDefault()
        clientConnect($(this));
        $('#submit-button').attr('disabled', 'disabled')
    });
});

function clientConnect(formElement) {
    var clientID = uuidv4();
    var data = getFormData(formElement);
    var socket = io.connect('//' + document.domain + ':' + location.port +
        '/classify?clientID=' + clientID,  {'forceNew': true});

    socket.on('connect', function(){
        console.log("connected");

        socket.emit('compute', clientID, data.algorithm, data.username, data.follower_limit,
            data.media_per_follower_limit, data.comments_per_media_limit, function(){
            console.log("Requested computation using " + data.algorithm +
                " algorithm as " + clientID);
        });

        resetProgress();
    })

    socket.on(clientID, function(msg) {
        if(msg.type == "data") {
            console.log("Received data\n" + msg.header + ":\n" + msg.body);

            var data = "";
            if(msg.body != "") {
                data = msg.header + ": " + msg.body;
            } else {
                data = msg.header;
            }

            var ul = document.getElementById("progress-msg");
            var li = document.createElement("li");
            li.appendChild(document.createTextNode(data));
            li.setAttribute("class", "list-group-item");
            ul.appendChild(li);
        }

        if(msg.type == "error") {
            showAlert(msg.header, msg.body)
        }

        if(msg.done == "true"){
            if(msg.type == "error") {
                finishProgress();
                socket.disconnect();

                return;
            }

            var extras = msg.extra.split(',');
            var extra_username = extras[0];
            var extra_processing_time = extras[1];
            var extra_pic_url = extras[2];
            var extra_male_count = parseInt(extras[3]);
            var extra_female_count = parseInt(extras[4]);

            finishProgress();

            $('#result-title').html(extra_username);
            $('#result-body').html(msg.body);
            $('#processing-time').html(extra_processing_time);
            $('#result-pic').attr('src', extra_pic_url);
            $('#result-url').attr('href', '//instagram.com/' + extra_username + '/');

            var chartCtx = $("#result-chart");
            var chartData = {
                labels: ['Male', 'Female'],
                datasets: [{
                    label: 'Gender percentange',
                    data: [extra_male_count, extra_female_count],
                    backgroundColor: [
                        'rgba(60, 210, 255, 255)',
                        'rgba(255, 149, 235, 255)'
                    ]
                }]
            }
            var chartOpt = {
                plugins: {
                    datalabels: {
                        formatter: (value, ctx) => {
                            let sum = 0;
                            let dataArr = ctx.chart.data.datasets[0].data;
                            dataArr.map(data => {
                                sum += data;
                            });
                            let percentage = (value*100 / sum).toFixed(2)+"%";
                            return percentage;
                        },
                        color: '#fff',
                        legend: {
                            display: false
                        }
                    }
                }
            }

            var result_chart = new Chart(chartCtx, {
                type: 'doughnut',
                data: chartData,
                options: chartOpt
            });

            $('#result').collapse('show');
            socket.disconnect();
        }else{
            var progress_message = msg.header;
            if(msg.body != '') {
                progress_message = progress_message + '  -  ' + msg.body;
            }
            $('#progress-bar-child').html(progress_message);
        }
    });
}

function showAlert(alerttype, message) {
    $('#alert-placeholder').append('<div id="alert" class="alert alert-' +  alerttype + '" role="alert"><a class="close" data-dismiss="alert">×</a><span>'+message+'</span></div>')

    setTimeout(function() {
        $("#alert").remove();
    }, 5000);
}

function finishProgress() {
    $('#progress-bar').hide();
    $('#submit-button').removeAttr('disabled');
}

function resetProgress() {
    $('#progress-msg li').remove();
    $('#progress').collapse('show');

    $('#progress-bar').show();
    $('.progress-bar')
    .css('width', '100%')
    .attr('aria-valuenow', 100);

    $('#result').collapse('hide');

    $('#data-log').html('');
    $('#data').collapse('show');
}

function getFormData(formElement) {
    var data = {}, inputs = formElement.serializeArray();
    $.each(inputs, function(i, o){
        data[o.name] = o.value;
    });

    return data
}

function checkProgress(clientID) {
    function worker() {
        $.get('progress/' + clientID, function(data) {
            if (progress < 100) {
                // progressBar.set_progress(progress)
                console.log("Progress: " + data)
                setTimeout(worker, 1000)
            }
        })
    }
}

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
}
