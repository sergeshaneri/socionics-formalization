function Header(el)
  local name = pandoc.utils.stringify(el.content)
  if el.level == 2 and (name:match("^8%.") or name:match("^9%.") or name:match("^10%.")
      or name:match("^Приложение ")) then
    return {pandoc.RawBlock("latex","\\clearpage"),el}
  end
  if el.level == 3 and name:match("^O%d") then
    return {pandoc.RawBlock("latex","\\clearpage"),el}
  end
  if el.level == 3 and name:match("^T%d") then
    local reserve = "20"
    if name:match("^T05%.") or name:match("^T22%.") or name:match("^T26%.") then reserve = "35" end
    return {pandoc.RawBlock("latex","\\Needspace{" .. reserve .. "\\baselineskip}"),el}
  end
  if el.level == 3 and name:match("^D%d") then
    return {pandoc.RawBlock("latex","\\Needspace{9\\baselineskip}"),el}
  end
end

function Para(el)
  local text = pandoc.utils.stringify(el.content)
  if text:match("^T%d%d%.%d%. ") then
    return {pandoc.RawBlock("latex","\\Needspace{5\\baselineskip}"),el}
  end
end

function Table(el)
  local n = #el.colspecs
  local header_cells = {}
  for _, row in ipairs(el.head.rows) do
    for _, cell in ipairs(row.cells) do
      table.insert(header_cells,pandoc.utils.stringify(cell.contents))
    end
  end
  local head = table.concat(header_cells," ")
  local widths = {}
  if n == 9 then
    widths = {0.16,0.105,0.105,0.105,0.105,0.105,0.105,0.105,0.105}
  elseif n == 4 then
    if head:find("Положительный") then widths = {0.055,0.28,0.565,0.10}
    elseif head:find("Класс точного") then widths = {0.55,0.15,0.15,0.15}
    elseif head:find("Исходный блок") then widths = {0.22,0.16,0.18,0.44}
    elseif head:find("iota") then widths = {0.12,0.13,0.36,0.39}
    elseif head:find("Минимальное число") then widths = {0.55,0.15,0.15,0.15}
    else widths = {0.40,0.20,0.20,0.20}
    end
  elseif n == 3 then
    if head:find("Полюс") then widths = {0.065,0.48,0.455}
    elseif head:find("Тетрада") then widths = {0.105,0.335,0.56}
    elseif head:find("ID") then widths = {0.105,0.20,0.695}
    else widths = {0.24,0.38,0.38}
    end
  elseif n == 2 then
    if head:find("Самостоятельное") then widths = {0.47,0.53}
    elseif head:find("Файл") then widths = {0.32,0.68}
    else widths = {0.28,0.72}
    end
  end
  if #widths == n then
    for i=1,n do el.colspecs[i] = {pandoc.AlignLeft,widths[i]} end
  end
  local rows = #el.head.rows
  for _,body in ipairs(el.bodies) do rows = rows + #body.head + #body.body end
  local prefix = "\\begingroup\\small"
  if rows <= 17 then
    prefix = prefix .. "\\Needspace{" .. tostring((rows+1)*1.25) .. "\\baselineskip}"
  end
  return {pandoc.RawBlock("latex",prefix),el,pandoc.RawBlock("latex","\\endgroup")}
end
