// Получаем элемент canvas первого графика и контекст рисования
var ctx = document.getElementById('historical-chart').getContext('2d');

// Создаем объект первого графика
var cpuHistoricalChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: 'Текущая загрузка',
      data: [],
      borderColor: 'blue',
      fill: false
    }]
  },
  options: {
    responsive: false,
    title: {
      display: true,
      text: 'История изменения моментальной загрузки процессора'
    },
    scales: {
      xAxes: [{
        type: 'time',
        distribution: 'series',
        ticks: {
          source: 'labels'
        },
        time: {

              displayFormats: {
                'day': 'HH:SS'
              }
            }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});

// Функция для обновления данных на первом графике
function updateHistoricalChart() {
  fetch('/get-historical-data')
    .then(response => response.json())
    .then(data => {
      cpuHistoricalChart.data.labels = data.x;
      cpuHistoricalChart.data.datasets[0].data = data.y;
      cpuHistoricalChart.update();
    });
};

// Обновляем первый график каждые 5 секунд
setInterval(updateHistoricalChart, 5000);

/* --- */

// Получаем элемент canvas второго графика и контекст рисования
var ctx = document.getElementById('average-chart').getContext('2d');

// Создаем объект графика
var cpuAverageChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: 'Усредненная загрузка процессора ',
      data: [],
      borderColor: 'red',
      fill: false
    }]
  },
  options: {
    responsive: false,
    title: {
      display: true,
      text: 'График усредненной загрузки процессора'
    },
    scales: {
      xAxes: [{
        type: 'time',
        distribution: 'series',
        ticks: {
          source: 'labels'
        }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});

// Функция для обновления данных на графике
function updateAverageChart() {
  fetch('/get-average-data')
    .then(response => response.json())
    .then(data => {
      cpuAverageChart.data.labels = data.x;
      cpuAverageChart.data.datasets[0].data = data.y;
      cpuAverageChart.update();
    });
};

// Обновляем график каждые 60 секунд
setInterval(updateAverageChart, 60000);

