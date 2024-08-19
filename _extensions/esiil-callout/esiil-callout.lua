function Div(el)
    if el.classes:includes('callout-read') then
        local title = "Read More"
        if el.attributes.title then
            title = title .. ': ' .. el.attributes.title
        end
        -- Create a callout with a custom type
        return quarto.Callout({
            -- Define the type of callout
            type = "read", 
            -- Callout title     
            title = title,
            -- This is broken right now; overriding in CSS
            icon = true,
            -- Set the appearance: minimal, simple, default
            appearance = "default", 
            -- Pass content through
            content = el.content 
        })

    elseif el.classes:includes('callout-video') then
        -- Create a callout with a custom type
        return quarto.Callout({
            type = "video",          
            title = "Check out our demo video!",   
            icon = true,
            appearance = "default",
            content = el.content
        })

    elseif el.classes:includes('callout-respond') then
        return quarto.Callout({
            type = "respond",
            title = "Reflect and Respond",    
            icon = true,
            appearance = "default",
            content = el.content
        })

    elseif el.classes:includes('callout-discuss') then
        return quarto.Callout({
            type = "discuss",
            title = "Conversation Starter",
            icon = true,
            appearance = "default",
            content = el.content
        })

    elseif el.classes:includes('callout-task') then
        local title = "Try it"
        if el.title then
            title = title .. ': ' .. el.title
        end
        return quarto.Callout({
            type = "task",
            title = "Let's Try It!",
            icon = true,
            appearance = "default",
            content = el.content
        })

    elseif el.classes:includes('callout-extra') then
        return quarto.Callout({
            type = "extra",
            title = "Looking for an Extra Challenge?",
            icon = true,
            appearance = "default",
            content = el.content
        })

    else
        return el
    end
end
