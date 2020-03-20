// Java code for the QC plots.

/** Helper for creating tick labels for large numbers. */
function largeValueTick(value, _index, _values) {
  if (value > 1000 * 1000 && value % (1000 * 1000) == 0) {
    return Math.round(value / 1000 / 1000) + "M"
  } else if (value > 1000 && value % 1000 == 0) {
    return Math.round(value / 1000) + "k"
  } else if (value > 1000 && value % 500 == 0) {
    return (value / 1000).toFixed(1) + "k"
  } else {
    return value
  }
}

/** Helper for creating tooltip labels for large values. */
function largeValueLabel(tooltipItem, data) {
  let label = data.datasets[tooltipItem.datasetIndex].label || ''
  if (label) {
    label += ": "
  }

  if (tooltipItem.yLabel > 1000 * 1000) {
    label += (tooltipItem.yLabel / 1000 / 1000).toFixed(2) + "M"
  } else if (tooltipItem.yLabel > 1000) {
    label += (tooltipItem.yLabel / 1000).toFixed(2) + "k"
  } else {
    label += tooltipItem.yLabel
  }

  return label
}

/** Plot variant types. */
function plotlyVariantTypes(response, containerId) {
    const seq = palette('tol', response.data.variantTypeData.length)
    const varTypeData = response.data.variantTypeData.map(function (item, index) {
      return {
        type: "bar",
        marker: {
          color: "#" + seq[index],
          line: {
            color: "#" + seq[index],
          }
        },
        ...item
      }
    })

    const layout = {
      title: {
        text: 'Variant types',
      },
      yaxis: {
        automargin: true,
        autorange: true,
      },
      xaxis: {
        automargin: true,
        autorange: true,
      },
    }

    $("#" + containerId + " .placeholder-container").remove()
    Plotly.newPlot(containerId, varTypeData, layout, {responsive: true})
}

/** Plot selected variant effects. */
function plotlyVariantEffects(response, containerId) {
    const seq = palette('tol', response.data.variantEffectData.length)

    const varEffects = [
      "synonymous",
      "missense",
      "UTR",
      "splc. region",
      "splc. motif",
      "start lost",
      "nonsense",
      "stop lost",
      "infrm. indel",
      "frameshift"
    ]

    const barChartData = response.data.variantEffectData.map(function (item, index) {
      return {
        hovermode: "closest",
        showlegend: false,
        type: "bar",
        marker: {
          color: "#" + seq[index],
          line: {
            color: "#" + seq[index],
          },
        },
        ...item,
      }
    })

    const layout = {
      showlegend: true,
      title: {
        text: 'Variant effects',
      },
      yaxis: {
        automargin: true,
        autorange: true,
      },
      xaxis: {
        automargin: true,
        autorange: true,
      },
    }

    $("#" + containerId + " .placeholder-container").remove()
    Plotly.newPlot(containerId, barChartData, layout, {responsive: true})
}

function plotlyIndelSizes(response, containerId) {
  const seq = palette('tol', response.data.variantEffectData.length)

  const barChartData = response.data.indelSizeData.map(function (item, index) {
    return {
      type: 'bar',
      marker: {
        color: '#' + seq[index],
        line: {
          color: '#' + seq[index],
        }
      },
      ...item,
    }
  })

  const layout = {
    title: {
      text: 'Indel sizes'
    },
    xaxis: { type: 'category', automargin: true, autorange: true},
    yaxis: { automargin: true, autorange: true},
  }

  $("#" + containerId + " .placeholder-container").remove()
  Plotly.newPlot(containerId, barChartData, layout, {responsive: true})
}

/** Helper for creating tooltip labels for relatedness entries. */
function relatednessLabel(tooltipItem, data) {
  return data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index].sample0 + "-" +
    data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index].sample1
}

/** Convert foreground to background color (setting alpha to 0.2). */
function colorFgToBg(col) {
  return "rgb(" +
    parseInt(col.substring(0, 2), 16) + ", " +
    parseInt(col.substring(2, 4), 16) + ", " +
    parseInt(col.substring(4, 6), 16) + ", 0.2)"
}

/** Plot relatedness. */
function plotlyRelatedness(response, containerId) {
  const relData = response.data.relData
  if (relData.length === 0) {
    $("#" + containerId + " .placeholder-container .placeholder-text").html('<span class="text-muted"><i class="fa fa-ban fa-3x"></i><br /><p class="pt-3 font-italic">No relatedness plot available for a singleton.</p></span>');
    return;
  }
  const clsRelData = {
    sibSib: {x: [], y: [], text: []},
    parentChild: {x: [], y: [], text: []},
    other: {x: [], y: [], text: []}
  }
  for (var i = 0; i < relData.length; ++i) {
    let entry = null;
    if (relData[i].parentChild) {
      entry = clsRelData.parentChild
    } else if (relData[i].sibSib) {
      entry = clsRelData.sibSib
    } else {
      entry = clsRelData.other
    }
    entry.x.push(relData[i].ibs0)
    entry.y.push(relData[i].rel)
    entry.text.push(relData[i].sample0 + "-" + relData[i].sample1)
  }

  const pal = palette("mpn65", 4)
  const scatterPlotData = []
  if (clsRelData.sibSib.x.length) {
    scatterPlotData.push({
      type: "scattergl",
      mode: "markers",
      name: "sibling-sibling",
      hoverinfo: "text",
      marker: {
        size: 8,
        opacity: 0.8,
        color: colorFgToBg(pal[3]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[3]
        }
      },
      x: clsRelData.sibSib.x,
      y: clsRelData.sibSib.y,
      text: clsRelData.sibSib.text
    })
  }
  if (clsRelData.parentChild.x.length) {
    scatterPlotData.push({
      type: "scattergl",
      mode: "markers",
      name: "parent-child",
      hoverinfo: "text",
      marker: {
        size: 8,
        opacity: 0.8,
        color: colorFgToBg(pal[1]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[1]
        }
      },
      x: clsRelData.parentChild.x,
      y: clsRelData.parentChild.y,
      text: clsRelData.parentChild.text
    })
  }
  if (clsRelData.other.x.length) {
    scatterPlotData.push({
      type: "scattergl",
      mode: "markers",
      name: "other",
      hoverinfo: "text",
      marker: {
        size: 8,
        opacity: 0.8,
        color: colorFgToBg(pal[2]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[2]
        }
      },
      x: clsRelData.other.x,
      y: clsRelData.other.y,
      text: clsRelData.other.text
    })
  }

  const layout = {
    title: {
      text: 'Relatedness vs. IBS0'
    },
    showlegend: true,
    hovermode: 'closest',
    legend: {
      x: 0.7,
      y: 1
    },
    xaxis: {
      automargin: true,
      autorange: true,
      title: {
        text: 'IBS0 (vars without shared allele)'
      }
    },
    yaxis: {
      automargin: true,
      autorange: true,
      title: {
        text: 'relatedness coefficient'
      }
    },
  }

  $("#" + containerId + " .placeholder-container").remove()
  Plotly.newPlot(containerId, scatterPlotData, layout, {responsive: true})
}


function sexChrxHetHomLabel(item, data) {
  return data.datasets[item.datasetIndex].data[item.index].sample || "(unknown)"
}

/** Plot QC data for sex */
function plotlySexChrxHetHom(response, containerId) {
  const pal = palette("mpn65", 3)

  const ped = response.data.pedigree
  const sexErrors = response.data.sexErrors
  const chrXHetHomRatio = response.data.chrXHetHomRatio

  const dataOk = {x: [], y: [], text: []}
  const dataUnknown = {x: [], y: [], text: []}
  const dataError = {x: [], y: [], text: []}

  let seed = 1

  function random() {
    const x = Math.sin(seed++) * 10000
    return x - Math.floor(x)
  }

  ped
    .filter(function (line) { return line.has_gt_entries })
    .forEach(function (line) {
      if (line.sex == 0) {
        dataUnknown.x.push(1.5 + random() * 0.4 - 0.2)
        dataUnknown.y.push(chrXHetHomRatio[line.patient])
        dataUnknown.text.push(line.patient)
      } else if (line.patient in sexErrors) {
        dataError.x.push([1.5, 1.0, 2.0][line.sex] + random() * 0.4 - 0.2)
        dataError.y.push(chrXHetHomRatio[line.patient])
        dataError.text.push(line.patient)
      } else {
        dataOk.x.push([1.5, 1.0, 2.0][line.sex] + random() * 0.4 - 0.2)
        dataOk.y.push(chrXHetHomRatio[line.patient])
        dataOk.text.push(line.patient)
      }
    })

  const scatter = {
    type: "scattergl",
    mode: "markers",
    hoverinfo: "text",
  }

  const scatterPlotData = [
    {
      name: "OK",
      marker: {
        size: 8,
        opacity: 0.8,
        color: colorFgToBg(pal[2]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[2]
        }
      },
      ...scatter,
      ...dataOk
    },
    {
      name: "unknown",
      marker: {
        size: 8,
        opacity: 0.8,
        color: colorFgToBg(pal[1]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[1]
        }
      },
      ...scatter,
      ...dataUnknown
    },
    {
      name: "error",
      marker: {
        size: 8,
        opacity: 0.8,
        color: colorFgToBg(pal[0]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[0]
        }
      },
      ...scatter,
      ...dataError
    }
  ]

  const layout = {
    title: {
      text: 'Rate of het. calls on chrX'
    },
    showlegend: true,
    hovermode: 'closest',
    legend: {
      x: 0,
      y: 1
    },
    xaxis: {
      automargin: true,
      autorange: true,
      title: {
        text: 'sex from pedigree'
      },
      range: [0.6, 2.4],
      tickvals: [1.0, 1.5, 2.0],
      ticktext: ["male", "unknown", "female"]
    },
    yaxis: {
      automargin: true,
      autorange: true,
      title: {
        text: 'het./hom. alt. ratio'
      },
    },
  }

  $("#" + containerId + " .placeholder-container").remove()
  Plotly.newPlot(containerId, scatterPlotData, layout, {responsive: true})
}

function varDpLabel(item, data) {
  return data.datasets[item.datasetIndex].data[item.index].sample || "(unknown)"
}

/** Plot variant depth to het ratios. */
function plotlyVarDps(response, containerId) {
  const pal = palette("mpn65", 3)

  const dpQuantiles = response.data.dpQuantiles
  const dpIqr = dpQuantiles[3] - dpQuantiles[1]
  const hetRatioQuantiles = response.data.hetRatioQuantiles
  const hetRatioIqr = hetRatioQuantiles[3] - hetRatioQuantiles[1]

  const dataAll = response.data.dpHetData

  var dataOk = {x: [], y: [], text: []}
  var dataBadDp = {x: [], y: [], text: []}
  var dataBadRatio = {x: [], y: [], text: []}

  for (var i = 0; i < dataAll.length; ++i) {
    let data = dataAll[i]
    let dest = null
    if (Math.abs(dpQuantiles[2] - data.x) > 3 * dpIqr) {
      dest = dataBadDp
    } else if (Math.abs(hetRatioQuantiles[2] - data.y) > 3 * hetRatioIqr) {
      dest = dataBadRatio
    } else {
      dest = dataOk
    }
    dest.x.push(data.x)
    dest.y.push(data.y)
    dest.text.push(data.sample)
  }

  const scatter = {
    type: "scattergl",
    mode: "markers",
    hoverinfo: "text",
  }

  const scatterPlotData = [
    {
      name: "OK",
      marker: {
        opacity: 0.8,
        size: 8,
        color: colorFgToBg(pal[2]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[2]
        }
      },
      ...scatter,
      ...dataOk
    },
    {
      name: "depth outlier",
      marker: {
        opacity: 0.8,
        size: 8,
        color: colorFgToBg(pal[1]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[1]
        }
      },
      ...scatter,
      ...dataBadDp
    },
    {
      name: "ratio outlier",
      marker: {
        opacity: 0.8,
        size: 8,
        color: colorFgToBg(pal[0]),
        line: {
          opacity: 1.0,
          width: 1,
          color: "#" + pal[0]
        }
      },
      ...scatter,
      ...dataBadRatio
    }
  ]


  const layout = {
    title: {
      text: 'Depth and heterozygosity'
    },
    showlegend: true,
    hovermode:'closest',
    legend: {
      x: 0,
      y: 1
    },
    xaxis: {
      automargin: true,
      autorange: true,
      title: {
        text: 'median depth'
      },
    },
    yaxis: {
      automargin: true,
      autorange: true,
      title: {
        text: 'het. genotype ratio',
      },
      range: [0.0, 1.0],
    },
  }

  $("#" + containerId + " .placeholder-container").remove()
  Plotly.newPlot(containerId, scatterPlotData, layout, {responsive: true})
}
