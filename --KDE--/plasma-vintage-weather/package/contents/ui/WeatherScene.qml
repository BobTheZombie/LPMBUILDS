import QtQuick
import "WeatherApi.js" as Weather

Item {
    id: scene
    property int weatherCode: 2
    property bool isDay: true
    property bool animated: true
    property real phase: 0
    readonly property string sceneType: Weather.codeType(weatherCode)
    onWeatherCodeChanged: sky.requestPaint()
    onIsDayChanged: sky.requestPaint()
    onWidthChanged: sky.requestPaint()
    onHeightChanged: sky.requestPaint()
    onAnimatedChanged: sky.requestPaint()

    Timer {
        interval: 70
        repeat: true
        running: scene.visible && scene.animated
        onTriggered: {
            scene.phase += 1;
            sky.requestPaint();
        }
    }
    Canvas {
        id: sky
        anchors.fill: parent
        onPaint: {
            var ctx=getContext("2d"), w=width, h=height;
            if(w<=0||h<=0) return;
            ctx.clearRect(0,0,w,h);
            var grad=ctx.createLinearGradient(0,0,0,h);
            if(scene.isDay) {
                grad.addColorStop(0,scene.sceneType==="storm"?"#26344f":"#236a9e");
                grad.addColorStop(1,scene.sceneType==="storm"?"#52617b":"#a9d9ee");
            } else {
                grad.addColorStop(0,"#10182d"); grad.addColorStop(1,"#36456a");
            }
            ctx.fillStyle=grad;ctx.fillRect(0,0,w,h);
            var t=scene.animated?scene.phase:0;
            if(!scene.isDay){
                for(var s=0;s<24;s++){
                    var sx=((s*83+19)%100)/100*w,sy=((s*37+7)%80)/100*h;
                    ctx.fillStyle="rgba(255,249,222,"+(.25+.4*(.5+.5*Math.sin(s+t*.075)))+")";
                    ctx.beginPath();ctx.arc(sx,sy,1+(s%3)*.3,0,Math.PI*2);ctx.fill();
                }
            }
            var cloudy=scene.sceneType!=="sun";
            // Atmospheric sun / moon halo
            if(scene.isDay && scene.sceneType!=="storm") {
                var sunX=w*.72,sunY=h*.32;
                var halo=ctx.createRadialGradient(sunX,sunY,2,sunX,sunY,h*.56);
                halo.addColorStop(0,"rgba(255,247,199,.70)");
                halo.addColorStop(1,"rgba(255,247,199,0)");
                ctx.fillStyle=halo;ctx.fillRect(0,0,w,h);
                ctx.beginPath();ctx.arc(sunX,sunY,h*.175,0,Math.PI*2);
                ctx.fillStyle="#fff1be";ctx.fill();
            } else if(!scene.isDay){
                ctx.beginPath();ctx.arc(w*.72,h*.28,h*.14,0,Math.PI*2);
                ctx.fillStyle="#f1ebd3";ctx.fill();
                ctx.beginPath();ctx.arc(w*.76,h*.23,h*.14,0,Math.PI*2);
                ctx.fillStyle="#273652";ctx.fill();
            }
            function cloud(x,y,scale,alpha) {
                ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);
                ctx.globalAlpha=alpha;
                var cg=ctx.createLinearGradient(0,-48,0,26);
                cg.addColorStop(0,scene.isDay?"#ffffff":"#a9b5d3");
                cg.addColorStop(1,scene.isDay?"#dce6e8":"#596b8f");
                ctx.fillStyle=cg;
                ctx.beginPath();
                ctx.arc(-42,5,28,Math.PI,0);
                ctx.arc(-15,-12,32,Math.PI,0);
                ctx.arc(23,-17,37,Math.PI,0);
                ctx.arc(57,4,25,Math.PI,0);
                ctx.lineTo(57,29);ctx.lineTo(-42,29);ctx.closePath();ctx.fill();
                ctx.restore();
            }
            if(cloudy) {
                cloud(w*.21+(t*.20)%60-30,h*.38,h/185*.70,.88);
                cloud(w*.65-(t*.12)%55,h*.62,h/185*.91,.90);
                if(scene.sceneType==="cloud"||scene.sceneType==="storm")
                    cloud(w*.48+(t*.08)%45,h*.28,h/185*.59,.75);
            }
            if(scene.sceneType==="fog") {
                for(var f=0;f<4;f++) {
                    var fy=h*(.43+f*.14);
                    ctx.strokeStyle="rgba(244,248,247,.31)";ctx.lineWidth=h*.043;
                    ctx.beginPath();ctx.moveTo(-20,fy);
                    ctx.bezierCurveTo(w*.25,fy-7,w*.75,fy+9,w+20,fy);ctx.stroke();
                }
            }
            if(scene.sceneType==="rain"||scene.sceneType==="storm") {
                ctx.strokeStyle="rgba(197,230,255,.70)";ctx.lineWidth=1.8;
                for(var i=0;i<49;i++){
                    var x=(i*69.73+t*5.7)%(w+30)-15;
                    var y=(i*41.21+t*8.8)%(h+40)-20;
                    ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x-7,y+17);ctx.stroke();
                }
            }
            if(scene.sceneType==="snow") {
                for(var n=0;n<49;n++){
                    var px=(n*61.23+12+Math.sin((t+n)*.055)*12)%w;
                    var py=(n*47.81+t*(.46+(n%5)*.12))%(h+12);
                    ctx.beginPath();ctx.arc(px,py,1.7+n%3*.55,0,2*Math.PI);
                    ctx.fillStyle="rgba(255,255,255,.86)";ctx.fill();
                }
            }
            if(scene.sceneType==="storm" && Math.floor(t)%139<2 && scene.animated) {
                ctx.strokeStyle="rgba(255,239,179,.85)";ctx.lineWidth=3;
                ctx.beginPath();ctx.moveTo(w*.62,0);ctx.lineTo(w*.58,h*.3);
                ctx.lineTo(w*.67,h*.28);ctx.lineTo(w*.56,h*.75);ctx.stroke();
            }
            // Golden horizon streak echoes the analog bezel.
            var haze=ctx.createLinearGradient(0,h*.72,0,h);
            haze.addColorStop(0,"rgba(241,184,111,0)");
            haze.addColorStop(1,"rgba(240,184,111,.30)");
            ctx.fillStyle=haze;ctx.fillRect(0,h*.72,w,h*.28);
        }
    }
}
