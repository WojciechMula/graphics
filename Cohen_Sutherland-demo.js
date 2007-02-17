/*
	Cohen-Sutherland clipping demo
	Wojciech Mu³a, http://wmula.republika.pl/
	16-17.02.2007
*/

var point = null;

function OnMouseClick(ev) {
	var dm, xm, ym, dx, dy, d1, d2;
	
	if (point != null) {
		point = null;
		return;
	}
	dm = 30 * 30; // min dist

	xm = ev.clientX;
	ym = ev.clientY;

	dx = xm - x1;
	dy = ym - y1;
	d1 = dx*dx + dy*dy;
	
	dx = xm - x2;
	dy = ym - y2;
	d2 = dx*dx + dy*dy;

	point = null;
	if (d1 < dm || d2 < dm) {
		if (d1 < d2) point = 1;
		if (d2 < d1) point = 2;
	}
}

function OnMouseMotion(ev) {
	if (point == null) return;

	var xa, ya, xb, yb, iters;
	var x = ev.clientX;
	var y = ev.clientY;

	var line    = document.getElementById('line');
	var clipped = document.getElementById('clipped');
	var title = document.getElementById('status');

	if (point == 1) {
		line.setAttribute('x1', x);
		line.setAttribute('y1', y);
		x1 = x;
		y1 = y;
	}
	// point == 2
	else {
		line.setAttribute('x2', x);
		line.setAttribute('y2', y);
		x2 = x;
		y2 = y;
	}
	
	var r = Cohen_Sutherland(x1, y1, x2, y2, x_min, x_max, y_min, y_max);
	if (r != null) {
		line.setAttribute('stroke', 'black');
		[xa, ya, xb, yb, iters] = r; 
		clipped.style.display = "";
		clipped.setAttribute('x1', xa);
		clipped.setAttribute('y1', ya);
		clipped.setAttribute('x2', xb);
		clipped.setAttribute('y2', yb);
		if (iters == 1)
			title.textContent = '1 iteration';
		else
		if (iters == 0)
			title.textContent = 'inside';
		else
			title.textContent = iters + ' iterations';
	}
	else {
		line.setAttribute('stroke', 'red');
		clipped.style.display = "none";
		title.textContent = 'outside';
	}
}


function Cohen_Sutherland(xa,ya, xb,yb, x_min,x_max,y_min,y_max) {

	function code(x,y) {
		var b0, b1, b2, b3;
		b0 = (y > y_max);
		b1 = (y < y_min) << 1;
		b2 = (x > x_max) << 2;
		b3 = (x < x_min) << 3;
		return b0 | b1 | b2 | b3;
	}
	
	var code_a, code_b, code_o, code, iters;
	var x, y, t, xa, ya, xb, yb;
	
	function top(code)    {return (code & 0x01) != 0;}
	function bottom(code) {return (code & 0x02) != 0;}
	function left(code)   {return (code & 0x04) != 0;}
	function right(code)  {return (code & 0x08) != 0;}

	code_a = code(xa,ya);
	code_b = code(xb,yb);
	iters  = 0;
	while (true) {
		if (code_a == 0 && code_b == 0)
			return [xa, ya, xb, yb, iters];
	
		if ((code_a & code_b) != 0)
			return null;

		iters++;
	
		if (code_a != 0)
			code_o = code_a;
		else
			code_o = code_b;

		if (top(code_o)) {
			t = (y_max-ya)/(yb-ya);
			x = xa + t*(xb-xa);
			y = y_max;
		}
		else
		if (bottom(code_o)) {
			t = (y_min-ya)/(yb-ya);
			x = xa + t*(xb-xa);
			y = y_min;
		}
		else
		if (left(code_o)) {
			x = x_max;
			t = (x_max-xa)/(xb-xa);
			y = ya + t*(yb-ya);
		}
		else
		if (right(code_o)) {
			x = x_min;
			t = (x_min-xa)/(xb-xa);
			y = ya + t*(yb-ya);
		}

		if (code_o == code_a) {
			xa = x;
			ya = y;
			code_a = code(x,y);
		}
		else {
			xb = x;
			yb = y;
			code_b = code(x,y);
		}
	}
}

function setup_line(id, x1, x2, y1, y2) {
	var item = document.getElementById(id);
	item.setAttribute('x1', x1);
	item.setAttribute('x2', x2);
	item.setAttribute('y1', y1);
	item.setAttribute('y2', y2);
}

// Setup

// clipping area borders
var y_min = 50;
var y_max = 250;
var x_min = 200;
var x_max = 700-200;

// line coordinates
var x1=20, y1=80, x2=200, y2=100;

var item = document.getElementById("rect");
item.setAttribute('x', x_min);
item.setAttribute('y', y_min);
item.setAttribute('width',  x_max - x_min);
item.setAttribute('height', y_max - y_min);

setup_line('left',  x_min, x_min, -100, 400);
setup_line('right', x_max, x_max, -100, 400);
setup_line('top',    -100, 800, y_min, y_min);
setup_line('bottom', -100, 800, y_max, y_max);

x1 = x_max + 50;
x2 = x_max + 100;
y1 = y_min + 20;
y2 = y_max - 20;
setup_line('line', x1, x2, y1, y2);
	
document.getElementById("canvas").onclick = OnMouseClick;
document.getElementById("canvas").onmousemove = OnMouseMotion;

// vim: ts=4 sw=4 nowrap
