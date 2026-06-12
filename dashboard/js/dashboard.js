let temperatureSocket = null;
let pressureSocket = null;

let temperatureChart = null;
let pressureChart = null;

let statisticsSocket = null;

const MAX_POINTS = 100;

function createLineChart(elementId, title, unit) {
    const chart = echarts.init(document.getElementById(elementId));

    chart.setOption({
        title: {
            text: title,
            textStyle: {
                color: "#ffffff"
            }
        },
        tooltip: {
            trigger: "axis"
        },
        xAxis: {
            type: "category",
            data: [],
            axisLabel: {
                color: "#9ca3af"
            }
        },
        yAxis: {
            type: "value",
            name: unit,
            axisLabel: {
                color: "#9ca3af"
            }
        },
        series: [
            {
                name: title,
                type: "line",
                smooth: true,
                data: []
            }
        ],
        grid: {
            left: "10%",
            right: "5%",
            bottom: "15%"
        }
    });

    return chart;
}

function addPoint(chart, timestampNs, value) {
    const option = chart.getOption();

    const xData = option.xAxis[0].data;
    const yData = option.series[0].data;

    const timeLabel = new Date().toLocaleTimeString();

    xData.push(timeLabel);
    yData.push(value);

    if (xData.length > MAX_POINTS) {
        xData.shift();
        yData.shift();
    }

    chart.setOption({
        xAxis: {
            data: xData
        },
        series: [
            {
                data: yData
            }
        ]
    });
}

async function loadSensorDetails() {
    const response = await fetch("/sensors/details");
    const data = await response.json();

    return data.sensors;
}

function populateSelect(selectId, sensors) {
    const select = document.getElementById(selectId);

    select.innerHTML = "";

    sensors.forEach(sensor => {
        const option = document.createElement("option");
        option.value = sensor.sensor_id;
        option.textContent = `${sensor.sensor_id} (${sensor.location})`;
        select.appendChild(option);
    });
}

function connectSensorStream(sensorId, chart, valueElementId, unit) {
    const socket = new WebSocket(
        `ws://${window.location.host}/ws/samples/${sensorId}`
    );

    socket.onmessage = event => {
        const sample = JSON.parse(event.data);

        if (sample.type === "heartbeat") {
            return;
        }

        document.getElementById(valueElementId).textContent =
            `${sample.value.toFixed(3)} ${sample.unit}`;

        addPoint(chart, sample.timestamp_ns, sample.value);
    };

    socket.onopen = () => {
        console.log(`Connected to ${sensorId}`);
    };

    socket.onclose = () => {
        console.log(`Disconnected from ${sensorId}`);
    };

    return socket;
}



function connectStatisticsStream(sensorId) {
    if (statisticsSocket) {
        statisticsSocket.close();
    }

    statisticsSocket = new WebSocket(
        `ws://${window.location.host}/ws/statistics/${sensorId}`
    );

    statisticsSocket.onmessage = event => {
        const stats = JSON.parse(event.data);

        if (stats.type === "heartbeat") {
            return;
        }

        document.getElementById("stat-count").textContent =
            stats.count;

        document.getElementById("stat-min").textContent =
            stats.min.toFixed(3);

        document.getElementById("stat-max").textContent =
            stats.max.toFixed(3);

        document.getElementById("stat-avg").textContent =
            stats.avg.toFixed(3);
    };
}


async function initializeDashboard() {
    const sensors = await loadSensorDetails();

    const temperatureSensors = sensors.filter(sensor => sensor.unit === "C");
    const pressureSensors = sensors.filter(sensor => sensor.unit === "bar");

    populateSelect("temperature-sensor", temperatureSensors);
    populateSelect("pressure-sensor", pressureSensors);

    document.getElementById("sensor-count").textContent = sensors.length;

    temperatureChart = createLineChart(
        "temperature-chart",
        "Temperature",
        "°C"
    );

    pressureChart = createLineChart(
        "pressure-chart",
        "Pressure",
        "bar"
    );

    const temperatureSelect = document.getElementById("temperature-sensor");
    const pressureSelect = document.getElementById("pressure-sensor");

    function connectTemperature() {
        if (temperatureSocket) {
            temperatureSocket.close();
        }

        temperatureSocket = connectSensorStream(
            temperatureSelect.value,
            temperatureChart,
            "temperature-value",
            "°C"
        );

        connectStatisticsStream(temperatureSelect.value);
    }

    function connectPressure() {
        if (pressureSocket) {
            pressureSocket.close();
        }

        pressureSocket = connectSensorStream(
            pressureSelect.value,
            pressureChart,
            "pressure-value",
            "bar"
        );
    }

    temperatureSelect.addEventListener("change", connectTemperature);
    pressureSelect.addEventListener("change", connectPressure);

    connectTemperature();
    connectPressure();
}

initializeDashboard();