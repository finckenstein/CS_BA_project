function main(splash)
    assert(splash:go(splash.args.url))
    splash:wait(5)

    local get_element_dim_by_xpath = splash:jsfunc([[
        function(xpath) {
            var element = document.evaluate(xpath, document, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            var element_rect = element.getClientRects()[0];
            return {"x": element_rect.left, "y": element_rect.top}
        }
    ]])

    local agree_and_accept = get_element_dim_by_xpath(
        '//button[contains(@class, "css-15dhgct") and contains(text(), "AGREE  & EXIT")]')
    splash:set_viewport_full()
    splash:mouse_click(agree_and_accept.x, agree_and_accept.y)
    splash:wait(5)

    return {
        html = splash:html()
    }
end