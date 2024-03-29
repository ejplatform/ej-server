var conversation_id = 0;
var conversation_slug = "";

function setDateFilter() {
  let today = new Date();
  let sevenDaysBefore = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
  document.getElementById("end-date").value = formatDate(today);
  document.getElementById("start-date").value = formatDate(sevenDaysBefore);
}

function formatDate(date) {
  return date.toISOString().slice(0, 10);
}

function listenToDateChanges() {
  let startDateInput = document.getElementById("start-date");
  let endDateInput = document.getElementById("end-date");

  startDateInput.onchange = updateVisualization;
  endDateInput.onchange = updateVisualization;
}

function showLoading() {
  document.querySelector(".card-body-content-loading").style.display = "block";
}

function hideLoading() {
  document.querySelector(".card-body-content-loading").style.display = "none";
}

async function updateVisualization() {
  if (startDateIsBiggerThenEndDate()) {
    showErrors("invalid-dates");
    return;
  }
  hideErrors();
  showLoading();
  var voteData = await requestData();
  hideLoading();
  d3jsVisualization(voteData);
}

async function loadVoteVisualization(conversationId, conversationSlug) {
  conversation_id = conversationId;
  conversation_slug = conversationSlug;
  setDateFilter();
  listenToDateChanges();
  showLoading();
  var voteData = await requestData();
  hideLoading();
  d3jsVisualization(voteData);
}

function parseDate(voteData) {
  return voteData.data.map((d) => ({
    date: Date.parse(d.date),
    value: d.value,
  }));
}

function startDateIsBiggerThenEndDate() {
  var startDate = document.getElementById("start-date").value;
  var endDate = document.getElementById("end-date").value;
  return startDate > endDate;
}

function showErrors() {
  document.querySelector(".card-body-error-invalid-dates").style.display =
    "block";
}

function hideErrors() {
  document.querySelector(".card-body-error-invalid-dates").style.display =
    "none";
}

async function requestData() {
  var startDate = document.getElementById("start-date").value;
  var endDate = document.getElementById("end-date").value;

  var url =
    `/conversations/${conversation.id}/${conversation.slug}/report/votes-over-time?startDate=` +
    startDate +
    "&endDate=" +
    endDate;
  var response = await fetch(url);
  var data = await response.json();

  if (data.error) {
    showErrors();
    return {};
  }

  return parseDate(data);
}

// Copyright 2021 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/area-chart
function AreaChart(voteData, color) {
  const curve = d3.curveLinear;
  const margin = { top: 20, right: 30, bottom: 30, left: 40 };

  let width = d3.select("#votes-over-time").attr("width");
  let height = d3.select("#votes-over-time").attr("height");

  const X = voteData.map((d) => d.date);
  const Y = voteData.map((d) => d.value);
  const I = d3.range(X.length);

  const xScale = d3
    .scaleUtc()
    .domain(d3.extent(voteData, (d) => d.date))
    .range([margin.left, width - margin.right]);

  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(voteData, (d) => d.value)])
    .nice()
    .range([height - margin.bottom, margin.top]);

  const xAxis = d3
    .axisBottom(xScale)
    .ticks(width / 80)
    .tickSizeOuter(0);
  const yAxis = d3.axisLeft(yScale).ticks(height / 40);

  const D = voteData.map((d, i) => {
    return !isNaN(X[i]) && !isNaN(Y[i]);
  });

  const area = d3
    .area()
    .defined((i) => D[i])
    .curve(curve)
    .x((i) => xScale(X[i]))
    .y0(yScale(0))
    .y1((i) => yScale(Y[i]));

  let previusSvg = d3.select("#votes-over-time");
  previusSvg.remove();

  let svg = d3
    .select("#svg-container")
    .append("svg")
    .attr("id", "votes-over-time")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height]);

  svg
    .append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(yAxis)
    .call((g) => g.select(".domain").remove())
    .call((g) =>
      g
        .selectAll(".tick line")
        .clone()
        .attr("x2", width - margin.left - margin.right)
        .attr("stroke-opacity", 0.1)
    );

  svg.append("path").attr("fill", color).attr("d", area(I));

  svg
    .append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(xAxis);

  return svg.node();
}

async function d3jsVisualization(voteData) {
  AreaChart(voteData, "#042A46");
}

function showDatePickers() {
  let startDate = document.getElementById("start-date");
  let endDate = document.getElementById("end-date");
  startDate.addEventListener("click", () => {
    startDate.showPicker();
  });
  endDate.addEventListener("click", () => {
    endDate.showPicker();
  });
}
