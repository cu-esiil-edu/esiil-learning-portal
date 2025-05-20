local function base64_encode(data)
  local b = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
  return ((data:gsub('.', function(x)
    local r, b_val = '', x:byte()
    for i = 8, 1, -1 do r = r .. (b_val % 2^i - b_val % 2^(i-1) > 0 and '1' or '0') end
    return r
  end) .. '0000'):gsub('%d%d%d?%d?%d?%d?', function(x)
    if #x < 6 then return '' end
    local c = 0
    for i = 1, 6 do c = c + (x:sub(i, i) == '1' and 2^(6 - i) or 0) end
    return b:sub(c + 1, c + 1)
  end) .. ({ '', '==', '=' })[#data % 3 + 1])
end

-- Join and normalize the image path
local function get_normalized_image_path(project_root, src)
  local sep = package.config:sub(1, 1)
  local path

  if src:sub(1, 1) == "/" then
    path = table.concat({ project_root, src:sub(2) }, sep)
  else
    path = src
  end

  -- Normalize POSIX slashes to Windows if needed
  if sep == "\\" then
    path = path:gsub("/", "\\")
  end

  return path
end


function Image(el)
  local src = el.src

  if src:match("^https?://") or src:match("^data:") then
    return nil
  end

  -- Resolve absolute path to image
  local project_root = os.getenv("QUARTO_PROJECT_DIR") or "."
  local src_path = get_normalized_image_path(project_root, el.src)

  -- If root-relative (/img/foo.png), resolve from project root
  if src:sub(1, 1) == "/" then
    src_path = project_root .. src
  else
    -- Otherwise, assume it's already relative to current working dir
    src_path = src
  end

  local f = io.open(src_path, "rb")
  if not f then
    io.stderr:write("⚠️ Could not open image: " .. src_path .. "\n")
    return nil
  end

  local data = f:read("*all")
  f:close()

  local ext = src_path:match("^.+%.([^.]+)$")
  local mime_type = ({
    png = "image/png",
    jpg = "image/jpeg",
    jpeg = "image/jpeg",
    gif = "image/gif",
    svg = "image/svg+xml"
  })[ext] or "application/octet-stream"

  local encoded = base64_encode(data)
  el.src = "data:" .. mime_type .. ";base64," .. encoded
  return el
end
