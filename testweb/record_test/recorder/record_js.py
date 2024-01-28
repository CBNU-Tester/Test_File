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
            var csrfToken = getCookie('csrftoken');
            console.log(csrfToken);
            $.ajax({
                url: 'https://127.0.0.1:8000/records/components/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({'xpath': xpath }),
                headers: {
                    'X-CSRFToken': csrfToken
                },
                success: function (response) {
                    console.log('Request successful:', response);
                },
                error: function (error) {
                    console.error('Error in the request:', error);
                }
            });
            console.log('Clicked Element XPath:', xpath);
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

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    """
    return xpath_js

def execute_jquery():
    jquery_js="""
    javascript:(function() {
        function l(u, i) {
            var d = document;
            if (!d.getElementById(i)) {
                var s = d.createElement('script');
                s.src = u;
                s.id = i;
                d.body.appendChild(s);
            }
        }
        l('//code.jquery.com/jquery-3.2.1.min.js', 'jquery')
    })();
    """
    return jquery_js