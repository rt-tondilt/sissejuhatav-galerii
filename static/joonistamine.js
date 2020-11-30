
let t = 0;

function joonista() {
    var c = document.getElementById("taust");
    var ctx = c.getContext("2d");
    const { width, height } = c.getBoundingClientRect();
    c.width = width;
    c.height = height; 
    //console.log(width, height)
    ctx.scale(width/100, height/100);
    t;
    console.log(t)

    ctx.fillStyle = '#ff0000';
    ctx.fillRect(0, 0, 100, 100);
    s = 1;
    n =50;
    for (const xx of [(x)=>50+x+10, (x)=>50-x-10]) {
        for (let i = 0; i < n; i++) {
            //if (i!=t%10) {continue;}
            x = (x) => xx((i+x*2*(1+Math.sin(t/500)*3)) * 100/n);
            f = Math.sin(t/50)*10*s;
            ctx.beginPath();
            ctx.moveTo(x(1), 50);
            ctx.lineTo(x(0.5), 80+f);
            ctx.lineTo(x(0), 50);
            ctx.lineTo(x(0.5), 20+f);
            ctx.closePath();
            ctx.stroke();
            s = - s;    
        }
    }
    
    t++;
}

window.onload = () => {
    console.log('UU')
    window.setInterval(joonista, 100)
};