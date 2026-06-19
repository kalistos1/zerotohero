'use strict';

$(document).ready(function () {


  // Revenue Chart
  if ($('#revenue-chart').length > 0) {

    var options = {
      series: [{
        name: 'Revenue',
        data: [70, 155, 105, 70, 40, 85, 125, 95, 65, 90, 55, 75]
      }],

      chart: {
        height: 410,
        type: 'bar',
        toolbar: { show: false }
      },

      plotOptions: {
        bar: {
          borderRadius: 4,
          borderRadiusApplication: 'end', // 🔥 top only
          columnWidth: '65%'
        }
      },

      dataLabels: {
        enabled: false
      },

      xaxis: {
        categories: [
          'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ],
        axisBorder: { show: false },
        axisTicks: { show: false },
        labels: {
          style: {
            colors: '#545454',
            fontSize: '13px'
          }
        }
      },

      /* 🔥 LEFT SIDE AMOUNT STYLE */
      yaxis: {
        min: 0,
        max: 180,
        tickAmount: 9, // 0 → 180 in steps
        labels: {
          formatter: function (val) {
            if (val === 0) return '0';
            return '$' + val + 'K';
          },
          style: {
            colors: '#545454',
            fontSize: '13px'
          }
        }
      },

      grid: {
        borderColor: '#F5F6F8',
        strokeDashArray: 4,
        xaxis: { lines: { show: false } }
      },

      colors: ['#56BA99'],

      tooltip: {
        y: {
          formatter: function (val) {
            return '$' + val + 'K';
          }
        }
      }
    };

    var chart = new ApexCharts(
      document.querySelector("#revenue-chart"),
      options
    );

    chart.render();
  }


  // Call Chart
if ($('#call-chart').length > 0) {
    var options = {
        series: [
            { name: 'Inbound', data: [10, 19, 23, 10, 6, 19, 16, 15, 10, 15, 11, 16] },
            { name: 'Outbound', data: [-19, -12, -17, -10, -15, -13, -13, -6, -14, -7, -4, -13] }
        ],
        chart: {
            type: 'bar',
            height: 350,
            stacked: true,
            toolbar: { show: false },
            animations: { enabled: true, easing: 'easeinout', speed: 800 }
        },
        colors: ['#82C6B1', '#9D93FE'],
        stroke: { show: true, width: 4, colors: ['#fff'] },
        plotOptions: {
            bar: {
                borderRadius: 6,
                borderRadiusApplication: 'around',
                columnWidth: '60%', // Adjusted for better desktop spacing
            }
        },
        dataLabels: { enabled: false },
        grid: {
            borderColor: '#F1F1F1',
            strokeDashArray: 3,
            xaxis: { lines: { show: false } },
            yaxis: { lines: { show: true } }
        },
        yaxis: {
            min: -30, max: 30, tickAmount: 6,
            labels: {
                formatter: (val) => Math.abs(val),
                style: { colors: '#A0A0A0', fontSize: '12px' }
            }
        },
        xaxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            axisBorder: { show: false }, axisTicks: { show: false },
            labels: { style: { colors: '#545454', fontSize: '12px' } }
        },
        legend: { show: false },
        // 🔥 FULL RESPONSIVE SETTINGS
        responsive: [
            {
                breakpoint: 768, // Tablet
                options: {
                    plotOptions: { bar: { columnWidth: '80%' } },
                    yaxis: { labels: { show: true } }
                }
            },
            {
                breakpoint: 480, // Mobile
                options: {
                    chart: { height: 280 },
                    plotOptions: { bar: { columnWidth: '90%', borderRadius: 4 } },
                    xaxis: {
                        labels: {
                            rotate: -45, // Rotate months if they clash
                            style: { fontSize: '10px' }
                        }
                    }
                }
            }
        ]
    };
    var chart = new ApexCharts(document.querySelector("#call-chart"), options);
    chart.render();
}


 // Categories Chart
if ($('#categories-chart').length > 0) {
    var options = {
        series: [45, 15, 25, 15],
        chart: {
            height: 350,
            type: 'donut',
            animations: { enabled: true, easing: 'easeinout', speed: 800 }
        },
        colors: ['#DE3D8A', '#1E84FF', '#F47320', '#FFC107'],
        stroke: { show: true, width: 6, colors: ['#ffffff'] },
        plotOptions: {
            pie: {
                expandOnClick: false,
                donut: {
                    size: '80%',
                    labels: {
                        show: true,
                        name: { show: true, fontSize: '18px', color: '#DE3D8A', offsetY: -10 },
                        value: { show: true, fontSize: '24px', fontWeight: 700, color: '#1A202C', offsetY: 10 },
                        total: { 
                            show: true, label: 'Finance', color: '#DE3D8A',
                            formatter: () => '45%'
                        }
                    }
                }
            }
        },
        dataLabels: { enabled: false },
        legend: {
            show: true,
            position: 'bottom',
            horizontalAlign: 'left',
            width: 290, // Desktop fixed width for 2x2 grid
            itemMargin: { horizontal: 20, vertical: 10 },
            markers: { width: 8, height: 8, radius: 12, offsetX: -5 },
            labels: { colors: '#718096' }
        },
        labels: ['Finance', 'Photography', 'Marketing', 'Design'],
        // 🔥 FULL RESPONSIVE SETTINGS
        responsive: [
            {
                breakpoint: 1024, // Smaller Desktops/Tablets
                options: {
                    legend: { width: 250, itemMargin: { horizontal: 10 } }
                }
            },
            {
                breakpoint: 480, // Mobile
                options: {
                    chart: { height: 320 },
                    legend: { 
                        width: undefined, // Let it use full width
                        horizontalAlign: 'center', // Center on mobile
                        itemMargin: { horizontal: 10, vertical: 5 } 
                    },
                    plotOptions: {
                        pie: {
                            donut: {
                                labels: {
                                    name: { fontSize: '14px' },
                                    value: { fontSize: '18px' }
                                }
                            }
                        }
                    }
                }
            }
        ]
    };
    var chart = new ApexCharts(document.querySelector("#categories-chart"), options);
    chart.render();
}
});

