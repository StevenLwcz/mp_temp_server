window.onload = request_data();

setInterval(request_data, 360000); // 6 minutes

const C_HEIGHT = 220;
const C_WIDTH = 560;
// const X_AXIS = 25
const Y_AXIS = 200;
// const G_WIDTH = 600;
const G_HEIGHT = 200;
const G_MAX_NO = 250; // 2 pix per 6 mins 24 hrs

const getItem = idx => data => data[idx];
const mapItem = idx => data => [data[0], data[idx]];

// round up to the nearest increment
round_to_inc = (num, inc) =>
{
    x = Math.floor(num);
    while (x < num) x += inc;
    return x;
}

class Graph
{
    ctx;
    getFn;
    mn; // [date, min]
    mx; // [date, max]
    envData;
    startDate;
    endDate;
    height;
    width;
    x_axis;
    scale;
    dp;

    constructor(canvas, envData, idx)
    {
        this.envData = envData;
       // this.mapFn = mapItem(idx);
        this.getFn = getItem(idx);
        let c = document.getElementById(canvas);
        this.width = c.width;
        this.height = c.height;
        this.ctx = c.getContext("2d");
        this.ctx.font = "12px Arial";
        this.ctx.clearRect(0, 0, c.width, c.height);

        let mapFn = mapItem(idx);
        this.mn = mapFn(this.min());
        this.mx = mapFn(this.max());

        this.scale = this.getScale();

        this.dp = 1;
        if (this.scale <= 20)  this.dp = 0;
        if (this.scale >= 400) this.dp = 2;
        this.x_axis = this.ctx.measureText(this.mx[1].toFixed(this.dp)).width + 1;

        // console.log("min x: ", this.mn, " max:", this.mx, "scale:", this.scale, "dp", this.dp);
        this.startDate = new Date(envData[0][0] * 1000);
        this.endDate = new Date(envData[envData.length - 1][0] * 1000);
    }

    min() {
        return this.envData.reduce((a, b) => {
           return this.getFn(a) < this.getFn(b) ? a : b;
       });
    }

    max() {
        return this.envData.reduce((a, b) => {
           return this.getFn(a) > this.getFn(b) ? a : b;
       });
    }

    // 200 pixels
    getScale()
    {
        const diff = this.mx[1] - this.mn[1];
        if (diff <= 0.5)
            return 400;
        if (diff <= 1)
            return 200;
        if (diff <= 2)
            return 100;
        if (diff <= 3)
            return 66.6;
        if (diff <= 4)
            return 50;
        if (diff <= 5)
            return 40;
        if (diff <= 10)
            return 20;
        if (diff <= 20)
            return 10;
        if (diff <= 25)
            return 8;
        if (diff <= 50)
            return 4;
        if (diff <= 100)
            return 2;
        if (diff <= 150)
            return 1.33;
        if (diff <= 200)
            return 1;
       return 200 / diff;
    }

    axis(colour1 = "blue", colour2 = "lightblue")
    {
        // draw X Axis
        this.ctx.beginPath()
        this.ctx.strokeStyle = colour1
        this.ctx.lineWidth = 1;
        this.ctx.moveTo(this.x_axis, 0);
        this.ctx.lineTo(this.x_axis, C_HEIGHT);

        // draw Y Axis
        this.ctx.moveTo(0, Y_AXIS);
        this.ctx.lineTo(C_WIDTH, Y_AXIS)
        this.ctx.stroke();

        // draw X scale
        const inc = G_HEIGHT / (this.scale * 10);
        var temp = round_to_inc(this.mn[1], inc);

        this.ctx.beginPath()
        this.ctx.textBaseline = "bottom";
        this.ctx.strokeStyle = colour2
        this.ctx.lineWidth = 1;

        for (var y = 0; y < 10; y++)
        {
            var tempy = Y_AXIS - (temp - this.mn[1]) * this.scale;
            this.ctx.fillText(temp.toFixed(this.dp), 0, tempy);
            this.ctx.moveTo(this.x_axis + 1, tempy);
            this.ctx.lineTo(C_WIDTH, tempy);
            temp += inc;
        }
        
        this.ctx.stroke();

        // draw Y scale
        let hr = this.startDate.getHours();
        const mi = this.startDate.getMinutes();
        const z = this.x_axis + ((60 - mi)/ 60) * 20;  // 60/6 * 2
        const end = this.x_axis + G_MAX_NO * 2;
        if (mi != 0) hr++;
        if (hr == 24) hr = 0;

        this.ctx.beginPath()
        for (var x = z; x < end; x+=20)
        {
            this.ctx.fillText(hr, x, Y_AXIS + 14);
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, Y_AXIS - 1);
            hr++;
            if (hr == 24) hr = 0;
        }
        this.ctx.stroke();
    }

    drawGraph(colour = "blue")
    {
        if (this.envData.length < 2)
            return;

        let data = this.envData[0];
        let temp = this.getFn(data);
        data = this.envData[this.envData.length - 1];

        let tempy = Y_AXIS - (temp - this.mn[1]) * this.scale;

        this.ctx.beginPath()
        this.ctx.strokeStyle = colour;
        this.ctx.lineWidth = 1;

        let x = this.x_axis;
        this.ctx.moveTo(x, tempy);

        for (let d of this.envData.slice(1))
        {
            x = x + 2;
            temp = this.getFn(d); 
            tempy = Y_AXIS - (temp - this.mn[1]) * this.scale;
            this.ctx.lineTo(x, tempy);
        }

        this.ctx.stroke();
    }
}

function request_data() {

var request = new XMLHttpRequest();

request.open('GET', 'http://192.168.43.149:65510');
request.setRequestHeader("Accept", "application/json\r\n");

request.onload = function () {
    var response = request.response;
    var envData = JSON.parse(response);

    if (envData.length < 1)
    {
        document.getElementById("today").innerHTML = "No data avaliable";
        return;
    }

    const pos = envData.length > G_MAX_NO ? -G_MAX_NO : 0;
    envData = envData.slice(pos);

    var tg = new Graph("graph1", envData, 1);
    tg.axis();
    tg.drawGraph();

    const today = new Date();
    const mnd = new Date(tg.mn[0] * 1000);
    const mxd = new Date(tg.mx[0] * 1000);
    document.getElementById("today").innerHTML = "Today: " + today.toLocaleString();
    document.getElementById("tmin").innerHTML = `min: ${tg.mn[1].toFixed(tg.dp)}C at ${mnd.toLocaleString()}` +
                                           `<br\>max: ${tg.mx[1].toFixed(tg.dp)}C at ${mxd.toLocaleString()}`;
    document.getElementById("tdates").innerHTML = "Start: " + tg.startDate.toLocaleString() + 
                                               "<br\>End: " + tg.endDate.toLocaleString();

    var pg = new Graph("graph2", envData, 2);
    pg.axis("red", "pink");
    pg.drawGraph("red");

    var pg = new Graph("graph3", envData, 3);
    pg.axis("green", "lightgreen");
    pg.drawGraph("green");

    var pg = new Graph("graph4", envData, 4);
    pg.axis("purple", "plum");
    pg.drawGraph("purple");
}

request.send();

}
