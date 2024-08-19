function Div(el)
    -- Check if the div has a class that matches your custom callout type
    if el.classes:includes("custom-note") then
      -- Define the custom icon and color for the note
      local icon = pandoc.RawInline('html', '<i class="bi bi-eyeglasses"></i>') -- Example using Font Awesome
      local color = "lightblue"
      local title = "Note"  -- Default title for the note
  
      -- Insert the icon and title at the beginning of the block
      table.insert(el.content, 1, pandoc.Strong(pandoc.List{icon, pandoc.Space(), pandoc.Str(title)}))
      
      -- Apply custom styling to the block
      el.attributes['style'] = 'border-left: 4px solid ' .. color .. '; padding-left: 1em; margin-bottom: 1em;'
    end
  
    if el.classes:includes("custom-warning") then
      local icon = pandoc.RawInline('html', '<i class="fas fa-exclamation-triangle"></i>')
      local color = "orange"
      local title = "Warning"
  
      table.insert(el.content, 1, pandoc.Strong(pandoc.List{icon, pandoc.Space(), pandoc.Str(title)}))
      el.attributes['style'] = 'border-left: 4px solid ' .. color .. '; padding-left: 1em; margin-bottom: 1em;'
    end
  
    return el
  end
  


