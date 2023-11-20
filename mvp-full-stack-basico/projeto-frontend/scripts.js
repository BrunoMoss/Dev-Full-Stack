// Exemplo de código JavaScript para criar gráficos de barras e de linhas com D3.js
//document.addEventListener("DOMContentLoaded",function(){
// Dados de exemplo para o gráfico de barras
var barData = [
{ category: "Categoria 1", value: 30 },
{ category: "Categoria 2", value: 50 },
{ category: "Categoria 3", value: 20 }
];

// Largura e altura do gráfico de barras
var barWidth = 500;
var barHeight = 300;

// Criar uma escala para mapear os valores para a altura do gráfico de barras
var barYScale = d3.scaleLinear().domain([0, d3.max(barData, d => d.value)]).range([0, barHeight]);

// Selecionar o elemento SVG para o gráfico de barras
var barSvg = d3.select("#barChart")
.append("svg")
.attr("width", barWidth)
.attr("height", barHeight);

// Criar retângulos para as barras
barSvg.selectAll("rect")
.data(barData)
.enter()
.append("rect")
.attr("x", (d, i) => i * (barWidth / barData.length))
.attr("y", d => barHeight - barYScale(d.value))
.attr("width", barWidth / barData.length - 5)
.attr("height", d => barYScale(d.value))
.attr("fill", "#3498db");

// Adicionar rótulos para as barras
barSvg.selectAll("text")
.data(barData)
.enter()
.append("text")
.text(d => d.value)
.attr("x", (d, i) => i * (barWidth / barData.length) + (barWidth / barData.length) / 2)
.attr("y", d => barHeight - barYScale(d.value) - 5)
.attr("text-anchor", "middle")
.attr("fill", "#fff");

// Dados de exemplo para o gráfico de linhas
var lineData = [
{ series: "Série A", values: [10, 20, 30, 40, 50] },
{ series: "Série B", values: [50, 40, 30, 20, 10] }
];

// Largura e altura do gráfico de linhas
var lineWidth = 500;
var lineHeight = 300;

// Criar uma escala para mapear os valores para a largura do gráfico de linhas
var lineXScale = d3.scaleLinear()
.domain([0, lineData[0].values.length - 1])
.range([0, lineWidth]);

// Criar uma escala para mapear os valores para a altura do gráfico de linhas
var lineYScale = d3.scaleLinear()
.domain([0, d3.max(lineData, d => d3.max(d.values))])
.range([lineHeight, 0]);

// Selecionar o elemento SVG para o gráfico de linhas
var lineSvg = d3.select("#lineChart")
.append("svg")
.attr("width", lineWidth)
.attr("height", lineHeight);

// Criar linhas para as séries
var lineGenerator = d3.line()
.x((d, i) => lineXScale(i))
.y(d => lineYScale(d));

lineSvg.selectAll("path")
.data(lineData)
.enter()
.append("path")
.attr("d", d => lineGenerator(d.values))
.attr("fill", "none")
.attr("stroke", (d, i) => i === 0 ? "#3498db" : "#e74c3c")
.attr("stroke-width", 2);

// Adicionar eixos
var xAxis = d3.axisBottom(lineXScale);
var yAxis = d3.axisLeft(lineYScale);

lineSvg.append("g")
.attr("transform", "translate(0," + lineHeight + ")")
.call(xAxis);

lineSvg.append("g")
.call(yAxis)
//});
