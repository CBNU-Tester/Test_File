def get_xpath():
    xpath_js = """
        var blackBar = document.createElement('div');
        blackBar.style.position = 'fixed';
        blackBar.style.top = '0';
        blackBar.style.left = '0';
        blackBar.style.width = '100%';
        blackBar.style.height = '30px';
        blackBar.style.backgroundColor = 'black';
        blackBar.style.color = 'white';
        blackBar.style.padding = '5px';
        blackBar.style.boxSizing = 'border-box';
        blackBar.style.zIndex = '9999';
        blackBar.innerText = 'Element XPath: ';
        document.body.appendChild(blackBar);

        
        document.addEventListener('mousedown', function (event) {
            var clickedElement = event.target;

            var xpath = getXPath(clickedElement);

            console.log('Clicked Element XPath:', xpath);
            $.ajax({
                url: '{% url "components" %}',
                type: 'POST',
                data: JSON.stringify(xpath),
                contentType: 'application/json',
                success: function (response) {
                    console.log("실험 데이터 전송 성공")
                    //loadResult(response.processed_data_list)
                },
                error: function (error) {
                    console.log("실험 데이터 전송 실패")
                    console.error(error);
                }
            });
            return xpath;
        });


        document.addEventListener('mouseover', function (event) {
            var clickedElement = event.target;

            var xpath = getXPath(clickedElement);
            
            blackBar.innerText = 'Current Element XPath: ' + xpath;
            return xpath;
        });

        
        function getXPath(element) {
            if (element.id !== '')
                return 'id("' + element.id + '")';
            if (element === document.body)
                return element.tagName;

            var siblings = element.parentNode.childNodes;
            for (var i = 0; i < siblings.length; i++) {
                var sibling = siblings[i];
                if (sibling === element)
                    return getXPath(element.parentNode) + '/' + element.tagName + '[' + (i + 1) + ']';
            }
        }
    """
    return xpath_js

