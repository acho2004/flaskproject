    // Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}

// Area Chart Example
var ctx = document.getElementById("myAreaChart");
var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['8/1-8/7', '8/8-8/14', '8/15-8/21', '8/21-8/31'],
    datasets: [{
      label: "Earnings",
      lineTension: 0.3,
      backgroundColor: "rgba(78, 115, 223, 0.05)",
      borderColor: "rgba(78, 115, 223, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(78, 115, 223, 1)",
      pointBorderColor: "rgba(78, 115, 223, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
      pointHoverBorderColor: "rgba(78, 115, 223, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: [0,0,0,0],
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          maxTicksLimit: 5,
          padding: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '$' + number_format(value);
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': $' + number_format(tooltipItem.yLabel);
        }
      }
    }
  }
});


function getLearningDayCount(){
    let result = []
    $.ajax({
        type: "GET"
        , url: "/selectdb"
        , dataType: "json"
        , async: true
        , success: function (listData) {
            console.log(listData);

            console.log(listData[0]['created'].substring(8,10));
            var EI1 = 0, EI8 = 0,EI15 = 0, EI22 = 0, E1c = 0, E8c = 0, E15c = 0, E22c = 0;
            var holder = "";

            for (var i = 0; i < Object.keys(listData).length; i++){
                holder = listData[i]['created'].substring(8,10);
                console.log(holder);
                if(listData[i]['author_id'] != ){
                    continue;
                }
                if (parseInt(holder) <= 7){
                    EI1 += listData[i]['guess_MBTI_EI'];
                    E1c++;
                } else if (parseInt(holder) <= 14){
                    EI8 += listData[i]['guess_MBTI_EI'];
                    E8c++;
                }else if (parseInt(holder) <= 21){
                    EI15 += listData[i]['guess_MBTI_EI'];
                    E15c++;
                }else{
                    EI22 += listData[i]['guess_MBTI_EI'];
                    E22c++;
                }
            }
            if(E1c != 0)EI1 /= E1c;
            if(E8c != 0)EI8 /= E8c;
            if(E15c != 0)EI15 /= E15c;
            if(E22c != 0)EI22 /= E22c;
            myLineChart.reset();
            myLineChart.data.datasets[0].data = [EI1, EI8, EI15, EI22];
            myLineChart.data.labels = ['8/1-8/7', '8/8-8/14', '8/15-8/21', '8/22-8/31'];



            myLineChart.update();
        }
        , error: function (request,status,error) {
            alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
        }
    });

    return result;
}

window.onload = function(){
    getLearningDayCount()








}