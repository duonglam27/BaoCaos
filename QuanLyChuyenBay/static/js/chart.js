function drawRevenueChart(labels, data, colors, borderColors) {
    var ctx = document.getElementById('revenueStats').getContext('2d');
    var revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu',
                data: data,
                backgroundColor: colors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
