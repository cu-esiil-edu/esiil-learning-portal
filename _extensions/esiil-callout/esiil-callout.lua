function custom_callout(el, type, title)
    -- add
    if el.attributes.title then
        title = title .. ': ' .. el.attributes.title
    end
    -- Create a callout with a custom type
    callout = quarto.Callout({
        -- Define the type of callout
        type = type, 
        -- Callout title     
        title = title,
        -- This is broken right now; overriding in CSS
        icon = true,
        -- Set the appearance: minimal, simple, default
        appearance = "default", 
        -- Pass content through
        content = el.content 
    })
    return callout, title
end

function Div(el)
    local has_callout_class = false
    local type = 'default'
    for _, class in ipairs(el.classes) do
        class = class:gsub("[{}]", "")

        -- Check if the class starts with "callout-"
        if string.match(class, "^callout") then
            has_callout_class = true
        end
        local callout_type = string.match(class, "^callout%-(.+)")
        if callout_type then
            type = callout_type
        end
    end

    -- If no class starts with "callout", return element unchanged
    if not has_callout_class then
        return el
    end

    -- Get callout type if it's there
    local title = el.attributes.title

    -- Process custom callout types
    local callout
    if el.classes:includes('callout-read') then
        callout, title = custom_callout(el, type, "Read More")
    elseif el.classes:includes('callout-video') then
        callout, title = custom_callout(el, type, "Check out our demo video!")
    elseif el.classes:includes('callout-respond') then
        callout, title = custom_callout(el, type, "Reflect and Respond")
    elseif el.classes:includes('callout-discuss') then
        callout, title = custom_callout(el, type, "Conversation Starter")
    elseif el.classes:includes('callout-task') then
        callout, title = custom_callout(el, type, "Try It")
    elseif el.classes:includes('callout-extra') then
        callout, title = custom_callout(el, type, "Looking for an Extra Challenge?")
    else
        callout = el
    end
    
    if quarto.doc.is_format("ipynb") then

        -- Local styles.css file
        local css_path = './assets/styles.css'
        
        -- Start constructing the HTML
        local title_class
        if title then
            title_class = ' callout-titled '
        else
            title_class = ' '
        end

        local html_output
        html_output = '<link rel="stylesheet" type="text/css" href="' .. css_path .. '">'
        html_output = html_output ..'<div class="callout callout-style-default' .. title_class 
        html_output = html_output .. 'callout-' .. type .. '">'
        html_output = html_output .. '<div class="callout-header">'
        html_output = html_output .. '<div class="callout-icon-container">'
        html_output = html_output .. '<i class="callout-icon"></i>'
        html_output = html_output .. '</div>'
        if title then
            html_output = html_output .. '<div class="callout-title-container flex-fill">'
            html_output = html_output .. pandoc.write(pandoc.Pandoc(title), "html")
            html_output = html_output .. '</div>'
        end
        html_output = html_output .. '</div>'
        html_output = html_output .. '<div class="callout-body-container callout-body">'
        html_output = html_output .. pandoc.write(pandoc.Pandoc(el.content), "html")
        html_output = html_output .. '</div>'
        html_output = html_output .. '</div>'
        
        -- Return the raw HTML block
        return pandoc.Para({pandoc.RawInline('html', html_output)})
    else
        -- Return original callout it conditions aren't met
        return callout
    end
end