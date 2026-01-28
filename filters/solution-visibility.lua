local DEFAULT_HIDE_SOLUTIONS = {
  ["default"] = false,
  ["portal"] = false,
  ["release"] = false,
  ["student"] = true,
}

local function as_bool(value)
  if value == nil then
    return false
  end
  if type(value) == "boolean" then
    return value
  end
  if type(value) == "string" then
    return value == "true"
  end
  if type(value) == "table" then
    return pandoc.utils.stringify(value) == "true"
  end
  local value_type = pandoc.utils.type(value)
  if value_type == "MetaBool" then
    return value
  end
  if value_type == "MetaString" then
    return pandoc.utils.stringify(value) == "true"
  end
  return false
end

local profile = ""
local profile_hide = false
local function trim(value)
  return (value:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function first_profile(value)
  if not value or value == "" then
    return "default"
  end
  local token = value:match("^([^,%s]+)")
  if token and token ~= "" then
    return token
  end
  return value
end

local function is_solution_div(el)
  return el.classes and el.classes:includes("solution-code")
end

local function is_student_block(el)
  return el.classes and el.classes:includes("student-code")
end

local function handle_codeblock(el)
  if is_student_block(el) then
    el.classes = el.classes:filter(function(cls) return cls ~= "student-code" end)
    return pandoc.Div({el}, pandoc.Attr("", {"student-code"}, {}))
  end

  return el
end

local function handle_div(el)
  if not is_solution_div(el) then
    return nil
  end
  local updated = {}
  local applied = false
  for _, block in ipairs(el.content) do
    if block.t == "CodeBlock" then
      if profile_hide then
        -- Drop solution code but keep outputs.
      else
        if not applied then
          block.attributes["code-fold"] = block.attributes["code-fold"] or "true"
          block.attributes["code-summary"] = block.attributes["code-summary"] or "See our solution!"
          block.attributes["code-block-title"] = block.attributes["code-block-title"] or "SOLUTION"
          block.attributes["highlight"] = block.attributes["highlight"] or "true"
          applied = true
        end
        table.insert(updated, block)
      end
    else
      table.insert(updated, block)
    end
  end
  el.content = updated
  return el
end

local function resolve_profile_hide(meta_hide_solutions)
  if meta_hide_solutions == nil then
    return DEFAULT_HIDE_SOLUTIONS[profile]
  end

  local value_string = pandoc.utils.stringify(meta_hide_solutions)
  if value_string == "true" or value_string == "false" then
    return value_string == "true"
  end

  if type(meta_hide_solutions) == "table" then
    local direct_value = meta_hide_solutions[profile]
    if direct_value ~= nil then
      return as_bool(direct_value)
    end
  end

  if value_string and value_string ~= "" then
    for line in value_string:gmatch("[^\n]+") do
      local key, value = line:match("^%s*([%w%-_]+)%s*:%s*(%w+)%s*$")
      if key == profile and value then
        return value == "true"
      end
    end
  end

  return DEFAULT_HIDE_SOLUTIONS[profile]
end

function Pandoc(doc)
  profile = first_profile(trim(os.getenv("QUARTO_PROFILE") or "default"))
  local meta_hide_solutions = doc.meta["hide-solutions"] or doc.meta["hide_solutions"]
  profile_hide = resolve_profile_hide(meta_hide_solutions)

  return doc:walk({
    CodeBlock = handle_codeblock,
    Div = handle_div,
  })
end
