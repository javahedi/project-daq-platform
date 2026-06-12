let temperatureSocket = null;
let pressureSocket = null;

let temperatureStatsSocket = null;
let pressureStatsSocket = null;

let temperatureChart = null;
let pressureChart = null;

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

function resetChart(chart) {
    chart.setOption({
        xAxis: {
            data: []
        },
        series: [
            {
                data: []
            }
        ]
    });
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

async function loadSampleCount() {
    const response = await fetch("/samples/count");
    const data = await response.json();

    document.getElementById("sample-count").textContent = data.count;
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

function connectSensorStream(sensorId, chart, valueElementId) {
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
        console.log(`Sample stream connected: ${sensorId}`);
    };

    socket.onclose = () => {
        console.log(`Sample stream disconnected: ${sensorId}`);
    };

    return socket;
}

function connectStatisticsStream(sensorId, prefix) {
    const socket = new WebSocket(
        `ws://${window.location.host}/ws/statistics/${sensorId}`
    );

    socket.onmessage = event => {
        const stats = JSON.parse(event.data);

        if (stats.type === "heartbeat") {
            return;
        }

        document.getElementById(`${prefix}-stat-count`).textContent =
            stats.count;

        document.getElementById(`${prefix}-stat-min`).textContent =
            stats.min.toFixed(3);

        document.getElementById(`${prefix}-stat-max`).textContent =
            stats.max.toFixed(3);

        document.getElementById(`${prefix}-stat-avg`).textContent =
            stats.avg.toFixed(3);
    };

    socket.onopen = () => {
        console.log(`Statistics stream connected: ${sensorId}`);
    };

    socket.onclose = () => {
        console.log(`Statistics stream disconnected: ${sensorId}`);
    };

    return socket;
}

async function initializeDashboard() {
    const sensors = await loadSensorDetails();

    const temperatureSensors = sensors.filter(sensor => sensor.unit === "C");
    const pressureSensors = sensors.filter(sensor => sensor.unit === "bar");

    populateSelect("temperature-sensor", temperatureSensors);
    populateSelect("pressure-sensor", pressureSensors);

    document.getElementById("sensor-count").textContent = sensors.length;

    await loadSampleCount();

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

        if (temperatureStatsSocket) {
            temperatureStatsSocket.close();
        }

        resetChart(temperatureChart);

        temperatureSocket = connectSensorStream(
            temperatureSelect.value,
            temperatureChart,
            "temperature-value"
        );

        temperatureStatsSocket = connectStatisticsStream(
            temperatureSelect.value,
            "temperature"
        );
    }

    function connectPressure() {
        if (pressureSocket) {
            pressureSocket.close();
        }

        if (pressureStatsSocket) {
            pressureStatsSocket.close();
        }

        resetChart(pressureChart);

        pressureSocket = connectSensorStream(
            pressureSelect.value,
            pressureChart,
            "pressure-value"
        );

        pressureStatsSocket = connectStatisticsStream(
            pressureSelect.value,
            "pressure"
        );
    }

    temperatureSelect.addEventListener("change", connectTemperature);
    pressureSelect.addEventListener("change", connectPressure);

    connectTemperature();
    connectPressure();

    setInterval(loadSampleCount, 3000);
}

initializeDashboard();