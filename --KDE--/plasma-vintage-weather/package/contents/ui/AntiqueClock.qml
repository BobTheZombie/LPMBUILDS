import QtQuick

Item {
    id: clock
    property var dateTime: new Date()
    property bool showSeconds: true
    implicitWidth: 290
    implicitHeight: 290
    onDateTimeChanged: dial.requestPaint()
    onShowSecondsChanged: dial.requestPaint()

    Canvas {
        id: dial
        anchors.fill: parent
        antialiasing: true
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            var ctx = getContext("2d");
            var w = width, h = height;
            ctx.clearRect(0, 0, w, h);
            var cx = w / 2, cy = h / 2;
            var r = Math.max(1, Math.min(w, h) / 2 - 5);
            ctx.save();
            ctx.translate(cx, cy);
            // Outer brass bezel, individually shaded concentric rings.
            var bezel = ctx.createRadialGradient(-r*0.28, -r*0.34, r*0.12, 0, 0, r*1.04);
            bezel.addColorStop(0, "#fff0bb");
            bezel.addColorStop(0.50, "#b57a36");
            bezel.addColorStop(0.77, "#533b25");
            bezel.addColorStop(0.92, "#e6ba6a");
            bezel.addColorStop(1, "#36251c");
            ctx.beginPath(); ctx.arc(0, 0, r, 0, 2*Math.PI);
            ctx.fillStyle = bezel; ctx.fill();
            ctx.beginPath(); ctx.arc(0, 0, r*0.955, 0, 2*Math.PI);
            ctx.lineWidth = r*0.018; ctx.strokeStyle="#fff1b6"; ctx.stroke();
            var face = ctx.createRadialGradient(-r*.23,-r*.32,r*.04,0,0,r*.91);
            face.addColorStop(0,"#fffaf0");
            face.addColorStop(.55,"#f4e5ca");
            face.addColorStop(.85,"#d5b98d");
            face.addColorStop(1,"#9b7851");
            ctx.beginPath(); ctx.arc(0,0,r*.91,0,2*Math.PI);
            ctx.fillStyle=face; ctx.fill();
            ctx.beginPath(); ctx.arc(0,0,r*.825,0,2*Math.PI);
            ctx.lineWidth=r*.005; ctx.strokeStyle="#927047"; ctx.stroke();
            ctx.beginPath(); ctx.arc(0,0,r*.72,0,2*Math.PI);
            ctx.lineWidth=r*.0025; ctx.strokeStyle="rgba(87,58,35,.35)"; ctx.stroke();
            // Jewel-like minute markers.
            for (var i=0;i<60;i++) {
                var a=i*Math.PI/30-Math.PI/2;
                var major=i%5===0;
                var r1=r*(major?.773:.805), r2=r*.83;
                ctx.beginPath();
                ctx.moveTo(Math.cos(a)*r1,Math.sin(a)*r1);
                ctx.lineTo(Math.cos(a)*r2,Math.sin(a)*r2);
                ctx.strokeStyle=major?"#735332":"#b49468";
                ctx.lineWidth=major?r*.013:r*.004;
                ctx.stroke();
            }
            var roman=["XII","I","II","III","IV","V","VI","VII","VIII","IX","X","XI"];
            ctx.fillStyle="#37271b";
            ctx.textAlign="center"; ctx.textBaseline="middle";
            ctx.font="bold "+Math.round(r*.165)+"px Georgia, serif";
            for(var j=0;j<12;j++) {
                var angle=j*Math.PI/6-Math.PI/2;
                ctx.fillText(roman[j],Math.cos(angle)*r*.65,Math.sin(angle)*r*.65);
            }
            ctx.font="bold "+Math.round(r*.09)+"px Georgia, serif";
            ctx.fillStyle="#886a46";
            ctx.fillText("A U R O R A",0,-r*.34);
            ctx.font=Math.round(r*.075)+"px Georgia, serif";
            ctx.fillText("LPM  •  CHRONOS",0,r*.38);
            function hand(angle,length,back,width,color) {
                ctx.save();
                ctx.rotate(angle);
                ctx.beginPath();
                ctx.moveTo(-width*1.1,back);
                ctx.lineTo(-width*.52,-length*.82);
                ctx.lineTo(0,-length);
                ctx.lineTo(width*.52,-length*.82);
                ctx.lineTo(width*1.1,back);
                ctx.closePath(); ctx.fillStyle=color; ctx.fill();
                ctx.beginPath();
                ctx.moveTo(0,-length*.18);ctx.lineTo(0,-length*.82);
                ctx.strokeStyle="rgba(236,207,157,.62)";ctx.lineWidth=Math.max(1,width*.20);ctx.stroke();
                ctx.restore();
            }
            var d=clock.dateTime;
            var seconds=d.getSeconds()+d.getMilliseconds()/1000;
            var mins=d.getMinutes()+seconds/60;
            var hours=(d.getHours()%12)+mins/60;
            hand(hours*Math.PI/6,r*.47,r*.13,r*.048,"#352b22");
            hand(mins*Math.PI/30,r*.70,r*.13,r*.033,"#352b22");
            if(clock.showSeconds) {
                ctx.save(); ctx.rotate(seconds*Math.PI/30);
                ctx.beginPath();ctx.moveTo(0,r*.21);ctx.lineTo(0,-r*.77);
                ctx.lineWidth=r*.009; ctx.strokeStyle="#a3422c";ctx.stroke();
                ctx.beginPath();ctx.arc(0,-r*.59,r*.029,0,2*Math.PI);
                ctx.fillStyle="#a3422c";ctx.fill();
                ctx.restore();
            }
            ctx.beginPath();ctx.arc(0,0,r*.056,0,2*Math.PI);
            ctx.fillStyle="#3c2e23";ctx.fill();
            ctx.beginPath();ctx.arc(0,0,r*.025,0,2*Math.PI);
            ctx.fillStyle="#d9ab55";ctx.fill();
            // Glass reflection; subtle and translucent over the dial.
            ctx.beginPath();
            ctx.arc(-r*.13,-r*.20,r*.69,3.63,5.28,false);
            ctx.lineWidth=r*.04;ctx.strokeStyle="rgba(255,255,255,.15)";ctx.stroke();
            ctx.restore();
        }
    }
}
