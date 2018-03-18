/* UI control for the restock template (reporting/stock.html) */
/* make sure js/nouislider.js is in header */

var slider_actual_textinput = document.getElementById('sliderActualText');
var slider_stock_textinput = document.getElementById('sliderStockText');

var slider_actual = noUiSlider.create(document.getElementById('sliderActual'), {
	start: 10,
  step: 1,
	connect: [ true, false ],
	range: {
		'min': 0,
		'max': 30
	},
});

slider_actual.on("update", function(value){
  slider_actual_textinput.value = value.toString().split('.')[0];
});

slider_actual_textinput.addEventListener("change", function(){
  slider_actual.set(this.value);
});

var slider_stock = noUiSlider.create(document.getElementById('sliderStock'), {
	start: 10,
  step: 1,
	connect: [ true, false ],
	range: {
		'min': 0,
		'max': 30
	},
});

slider_stock.on("update", function(value){
  slider_stock_textinput.value = value.toString().split('.')[0];
});

slider_stock_textinput.addEventListener("change", function(){
  slider_stock.set(this.value);
});
