#!/usr/bin/env python3
#
# A *bookmark server* or URI shortener that maintains a mapping (dictionary)
# between short names and long URIs, checking that each new URI added to the
# mapping actually works (i.e. returns a 200 OK).
#
# This server is intended to serve three kinds of requests:
#
#   * A GET request to the / (root) path.  The server returns a form allowing
#     the user to submit a new name/URI pairing.  The form also includes a
#     listing of all the known pairings.
#   * A POST request containing "longuri" and "shortname" fields.  The server
#     checks that the URI is valid (by requesting it), and if so, stores the
#     mapping from shortname to longuri in its dictionary.  The server then
#     redirects back to the root path.
#   * A GET request whose path contains a short name.  The server looks up
#     that short name in its dictionary and redirects to the corresponding
#     long URI.
#
# Your job in this exercise is to finish the server code.
#
# Here are the steps you need to complete:
#
# 1. Write the CheckURI function, which takes a URI and returns True if a
#    request to that URI returns a 200 OK, and False otherwise.
#
# 2. Write the code inside do_GET that sends a 303 redirect to a known name.
#
# 3. Write the code inside do_POST that sends a 400 error if the form fields
#    are missing.
#
# 4. Write the code inside do_POST that sends a 303 redirect to the form
#    after saving a newly submitted URI.
#
# 5. Write the code inside do_POST that sends a 404 error if a URI is not
#    successfully checked (i.e. if CheckURI returns false).
#
# In each step, you'll need to delete a line of code that raises the
# NotImplementedError exception.  These are there as placeholders in the
# starter code.
#
# After writing each step, restart the server and run test.py to test it.

import http.server
import requests
import os
from urllib.parse import unquote, parse_qs

memory = {}

form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shortname">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''

form2 = '''<!DOCTYPE html>
<html>
    <head>
        <title>My HTML Notes</title>
        <style type="text/css">
            .rightAlignment{
                text-align: right;
            }
            h1{
                color: #15db95;
                font-family: serif;
            }
            h3{
                color: #0d19A3;
                padding: 0px;
                margin: 0px;
                font-family: serif;
            }
            p{
                margin-left: 10px;
                line-height: 18pt;
                /*color: #080f5b;   */          
            }
            li{
                margin-bottom: 5px; 
            }
            .small-list li{
                margin-bottom: 0px;
            }
            h4{
                margin: 0px;
                padding: 0px;
            }
            a{
                color: #c39022;
                text-decoration:none;
                font-weight: bold;
            }
            #sidebar a{
                display: block;
                text-decoration: none;
                text-align: center;
                padding: 20px;
                color: #080f5b;
                border-bottom: 2px solid #f4e4c1;
                background-color: inherit; 
            }
            #sidebar a.headline{
                padding: 20px;
                color: white;
                background-color: #080f5b; 
            }
            #sidebar a:hover{
                background-color: #10a26f;
            }
            #sidebar{
                position: fixed;
                left: 0px;
                top: 0px;
                width: 240px;
                height: 100%;
                /*padding: 20px;
                padding-top: 0px; */
                overflow: auto;/*
                background-color: #080f5b;*/
                background-color: #15db95;
            }
            #container{
                padding-left: 240px;
            }
            body{
                /*background-color: #eeeeee*/
                color: #080f5b;
                font-family: Verdana ;
                font-size: 11pt;
                line-height: 1.7
            }
            .section-box{
                border: 1px solid #dddddd;
                background-color: #eeeeee;
                padding: 5px;
                margin-bottom: 10px; 
            }
            strong{
                font-size: 13pt;
            }
            em{
                font-weight: bold;
            }
            .note-box{
                border: 1px solid #dddddd;
                background-color: #ffffff;
                padding: 5px;
                margin: 10px; 
            }
        </style>
    </head>
    <body>
        <div id="sidebar">
            <a href="#html-notes" class="headline">HTML Notes</a> 
            <a href="#markup">Format of markup</a>
            <a href="#other-elements">Some other elements</a>
            <a href="#nested-elements">Nested elements</a>
            <a href="#elements-types">Two types of elements</a>
            <a href="#division-element">Division element</a>
            <a href="#list-elements">List elements</a>
            <a href="#web-adresses">Web adresses</a>
            <a href="#anchor-element">Anchor element </a>
            <a href="#image-element">Image element</a>
            <a href="#relative-url">Relative URL</a>
            <a href="#doctype">DOCTYPE tag</a>
            <a href="#html-structure">HTML file structure</a>
            <a href="#validator">The validator</a>
            <a href="#css-notes" class="headline">CSS Notes</a>
            <a href="#developer-tool">Developer tool in browser</a>
            <a href="#dom-tree">HTML DOM tree</a>
            <a href="#css-code-type">Types of CSS code</a>
            <a href="#css-syntax">CSS Syntax</a>
            <a href="#selectors">Types of selectors</a>
            <a href="#selector-combining">Selectors combining</a>
            <a href="#cascading">Cascading</a>
            <a href="#units">Units</a>
            <a href="#boxes">Boxes</a>
            <a href="#colors">Colors</a>
            <a href="#fonts">Fonts</a>
            <a href="#display">Display Property</a>
            <a href="#position">position property</a>
            <a href="#more-css">More CSS</a>
        </div>
        <div id="container">
            <h1 id="html-notes">HTML Notes</h1>
            
            <!--i should rename this headline -->
            <div class="section-box">
                <h3 id="markup">Format of markup</h3>
                <ul>
                    <li>
                        <strong>HTML: </strong>hypertext markup language.
                    </li>
                    <li>
                        <strong>markup: </strong>is a text with special meaning tell the browser how to display text.
                    </li>
                    <li>
                        That is called an element <em>(note that there are some elements called void or empty consists of open tag only, like &lt;br> or &lt;img> elememnts).</em>
                    </li>
                    <li>
                        Break element <em>&lt;br></em> is used to break the line and start new line.
                    </li>
                </ul>
            </div>
            
            <!--i should rename this headline -->
            <div class="section-box">
                <h3 id="other-elements">Some other elements</h3>
                <ul>
                    <li>Mark element <mark>&lt;mark>.</mark></li>
                    <li>Subscript element <sub>&lt;sub>.</sub></li>
                    <li>Superscript element <sub>&lt;sub>.</suul></li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="nested-elements">Nested elements</h3>
                <ul>
                    <li>Elements can be nested but can't overlap.</li>
                    <li>Pragraph tag <em>&lt;p></em> can't be nested with other pragraph tag <em>&lt;p></em>.</li>
                </ul>
            </div>
            <div class="section-box">
                <h3>Two types of elements</h3> 
                <ul>
                    <li> 
                        Block <a href="https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements#Elements" title="reference to all block elements in html">Block elements</a>
                        <div class="note-box">
                            Block elements put invisiable box around the element, which has some priorities such as height, width and margine.
                        </div>
                    </li>
                    <li> 
                        Inline <a href=" https://developer.mozilla.org/en-US/docs/Web/HTML/Inline_elements#Elements" title="reference to all inline elements in html">Inline elements</a>
                    </li>                   
                </ul>                       
            </div>
            <div class="section-box">
                <h3 id="division-element"> Division element <em>&lt;div></em></h3>
                <ul>
                    <li>
                        It is a block element like pragraph element <em>&lt;p></em> and is used to divide the web page. It is usually used with CSS and may be used as a container.
                    </li>
                    <li>
                        Pragraph element <em>&lt;p></em> only contain inline elements and Text but Division element <em>&lt;div></em> is general and can be nested.
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="list-elements">List elements</h3>
                <ul>
                    <li>
                        There are two types of list elements.
                        <ol>
                            <li>order list &lt;ol>.</li>
                            <li>unorder list &lt;ul>.</li>
                        </ol>
                    </li>
                    <li>
                        Inside the list elements there are list item elements &lt;li>. It can't be outside list elements. list element has option closing tag and browser can guess the position of it by starting new list item &lt;li> or colosing tag for list element &lt;/ul> or &lt;/ol>.
                    </li>
                    <li>
                        Pragraph element also has option closing tag.
                    </li> 
                    <li>
                        List elements can't be nested in pragraph element.
                    </li> 
                </ul>
            </div>
            <div class="section-box">
                <h3>Web adresses <em>(URL)</em></h3>
                <ul>
                    <li>
                        Fully qualified URL consists of 3 compnents
                        <ol>
                            <li>Protocol: <em>http://, https:// or file://</em></li>
                            <li>Domain: <em>www.example.com</em></li>
                            <li>File path: <em>/local/notes.html</em></li>
                        </ol>
                    </li>
                    <li>
                        Ex: 
                        <ul>
                            <li>
                                http://en.wikipedia.org/<br>
                                There is no file path for home page of the website.
                            </li>
                            <li>
                                file:///Users/Kelly/notes.html<br>
                                There is no domain for file in local machine.
                            </li>
                        </ul> 
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3>Anchor element <em>&lt;a></em></h3>
                <ul>
                    <li>
                        This element is used to put hyperlinks.
                    </li>
                    <li>
                        Ex: &lt;a href="http://en.wikipedia.org/"> wiki &lt;/a>
                    </li>
                    <li>
                        The absolute URL of the hyperlink is put in href attribute in anchor element and should be fully qualified and the text that user will click on it to go to the URL destination is put as a text between opening and closing tag.
                    </li>
                    <li>
                        Attributes in HTML elements is inside the opning tag.
                    </li>
                    <li>
                        The format of attributes is Name=value Name=value <em>Ex: &lt;a href="http://en.wikipedia.org/" title="go to wikipedia"></em>.
                    </li>
                    <li>
                        We can use <a href="#relative-url">relative URL</a> in href attribute.
                    </li>
                    <li>
                        You can create a bookmark with anchor element by give the referenced element an id with id attribute and put the id value in href  attribute.
                    </li>
                    <li>
                        Ex: <em>&lt;h1 id="referenced element">headline&lt;/h1></em> then reference this element like this <em>&lt;a href="#referenced element">headline&lt;/a></em>.
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="image-element">Image element</h3>
                <ul>
                    <li>
                        Ex: &lt;img src="https://placebear.com/300/200" alt="bear image can,,t be loaded">
                    </li>
                    <li>
                        This example will display this image
                    </li>
                        <img src="https://placebear.com/300/200" alt="bear image can't be loaded">
                    </li>
                    <li>
                        The <em>src</em> attribute for the URL of image source and <em>alt</em> attribute for rhe tex will apper instead of the image if there is any problem to load the image
                    </li>
                    <li>
                        we can use the image element inside the anchor element instead of the text like this
                    </li>
                        -Ex: &lt;a href="https://www.google.com/" target="_blank"> &lt;img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" alt="google icon">&lt;/a>
                    </li>
                    <li>
                        This example will display this image link to google website<br>
                        <a href="https://www.google.com/" target="_blank"><img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" alt="google icon"></a>
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="relative-url">Relative URL</h3>
                <ul>
                    <li>
                        The value of The <em>src</em> attribute in image element and the <em>href</em> attribute in anchor element can be relative URL instead of fully qualified URL.
                    </li>
                    <li>
                        When the browser doesn't find protocol part, it consider it an relative address.
                    </li>
                    <li>
                        The fully qualified URL of relative address is the URL of current page without name of current file + the relative URL.
                    </li>
                    <li>
                        Ex if current page path is file:///D:/collage/summer%2019/web/udacity/notes.html and the relative URL is car.png 
                    </li>
                        then the final URL is file:///D:/collage/summer%2019/web/udacity/car.png
                    </li>
                    <li>
                        This example will display this image
                    </li>
                        <img src="car.png" alt="car image is not in the same folder of this file">
                </ul>
            </div>
            <div class="section-box">
                <h3 id="doctype">DOCTYPE tag</h3>
                <ul>
                    <li>
                        Tell the browser which kind of HTML in this file.
                    </li>
                    <li>
                        Put &lt;!DOCTYPE html> in the first line in the file for modern HTML.
                </ul>
            </div>
            <div class="section-box">
                <h3 id="html-structure">HTML file structure</h3>
                <p>
                    &lt;!DOCTYPE html><br>
                    &lt;html lang="en" &lt;!-- language of web page--> ><br>
                    &emsp;&lt;head><br>
                    &emsp;&emsp;&lt;!--in the head we put metadate about the web page like:--><br>
                    &emsp;&emsp;&lt;title>The titel of web page in the browser tap &lt;/title><br>
                    &emsp;&emsp;&lt;style>css for this file &lt;/style><br>
                    &emsp;&emsp;&lt;script>javascript code for frontend programming for this page &lt;/script><br>
                    &emsp;&lt;/head><br>
                    &emsp;&lt;body><br>
                    &emsp;&emsp;&lt;!-- the content of the page with prgraphs, images, videos, hyperlinks, etc.--><br>
                    &emsp;&lt;/body><br>
                    &lt;/html><br>
                </p>
            </div>
            <div class="section-box">
                <h3 id="validator">The validator</h3>
                <ul>
                    <li>
                        You can use this <a href=" https://validator.w3.org/" target="_blank">website</a> to validate your HTML file.
                    </li>
                </ul>
            </div>
            <!--####################################################################################################### -->
            <h1 id="css-notes">CSS Notes</h1>
            <div class="section-box">
                <strong>CSS:</strong> cascading style sheets.
            </div>
            <div class="section-box">
                <h3 id="developer-tool">Developer tool in browser</h3>
                <ul>
                    <li>
                        It view the source of the web page elements (HTML as displayed in the browser, CSS and script function).
                    </li>
                    <li>
                        You can edit the source in this tool and see the effect of that change.
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="dom-tree">HTML DOM tree</h3>
                <ul>
                    <li>
                        <strong>DOM: </strong> Document Object Model.
                    </li>
                    <li>
                        The HTML file can be represent as a tree.
                    </li>
                    <li>
                        The root of the tree is html element and have 2 children body and head.
                    </li>
                    <li>
                        The body have all components of web page as children.
                    </li>
                    <li>
                        Each child represent as invisible box and have smaller boxes inside it represent its children (nested elements).
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="css-code-type">Types of CSS code</h3>
                <ol>
                    <li>
                        <h4>Inline CSS</h4>
                        <ul>
                            <li>
                                It is the CSS wrote in style attribute of a HTML element.
                            </li>
                            <li>
                                This CSS is applied only to that element.
                            </li>
                            <li>
                                Ex: <em>&lt;p style="color:red; text-align:center;"> pragraph &lt;/ul></em>
                            </li>
                        </ul>
                    </li>

                    <li>
                        <h4>Embedded/Internal CSS</h4>
                        <ul>
                            <li>
                                It is wrote in the style element inside head element in html file.
                            </li>
                            <li>
                                This CSS is applied only to this HTML file.
                            </li>
                            <li>
                                Ex: <em>&lt;style> p{color:red; text-align:center;} &lt;/style></em>.
                            </li>
                            <li>
                                This example will applied to all pragraphes in this documents.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>External CSS</h4>
                        <ul>
                            <li>
                                It is wrote in external file with extention (.css).
                            </li>
                            <li>
                                To apply this code you sholud refrence it in the link element inside head element.
                            </li>
                            <li>
                                Ex: <em>&lt;link rel="stylesheet" href="font_shorthand_style.css"></em> for include CSS rules from file font_shorthand_style.css.
                            </li>
                        </ul>
                    </li>
                </ol>
            </div>
            <div class="section-box">
                <h3 id="css-syntax">CSS Syntax</h3>
                <ul>
                    <li>
                        The CSS external file or embedded CSS consist of one or more ruleset.
                    </li>
                    <li>
                        Each ruleset consist of group of selectors separated with , (declaration block){one or more declaration(rule) separated with ;}.
                    </li>
                    <li>
                        The selector determine which elements will the declaration applied on.
                    </li>
                    <li>
                        The declaration syntax is property:value.
                    </li> 
                    <li>
                        In inline CSS only we wrote the declarations.

                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="selectors">Types of selectors</h3>
                <ul>
                    <li>
                        <h4>Type selector</h4>
                        <ul>
                            <li>
                                To apply the css rules to a HTML element.
                            </li>
                            <li>
                                Ex <em>p { color: orange; }</em> will be applied to all pragraphs.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>Id selector</h4>
                        <ul>
                            <li>
                                To apply the css rules to an element which has the same value of selector for id attribute.
                            </li>
                            <li>
                                id attribute should have unique value.
                            </li>
                            <li>
                                Ex 
                            </li>
                                <em>
                                    #intro {<br>
                                    &emsp;color: white;<br>
                                    &emsp;background-color: gray;<br>
                                    }<br>
                                </em>
                                will be applied to id = "intro".
                            </li>
                            <li>
                                We put (#) before the class naame in selector.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>Class selector</h4>
                        <ul>
                            <li>
                                To apply the css rules to all elements which has the same value of selector for class attribute.
                            </li>
                            <li>
                                Many elements can have the same class value.
                            </li>
                            <li>
                                Ex <em> .first {font-size: 200%;}</em> will be applied to all elements with class = "first".
                            </li>
                            <li>
                                We put (.) before the class naame in selector.
                            </li>
                            <li>
                                The element can have multible classes in class attribute  separated with space to  apply rules from multible classes.
                            </li>
                            <li>
                                Ex <em>class ="intro first"</em> apply rules from intro and first classes.
                            </li>
                        </ul>               
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="selector-combining">Selectors combining</h3>
                <ul>
                    <li>
                        Ex
                        <ul>
                            <li>
                                <em>p .inter { color:red; }</em> apply to pragraph elements with class = "inter".
                            </li>
                            <li>
                                <em>li h1 #first{ color:red; } </em> apply to h1 inside li with id = "first".
                            </li>
                            <li>
                                <strong>Note that there are more types of selectors 
                                <a href="https://developer.mozilla.org/en-US/docs/Learn/CSS/Introduction_to_CSS/Selectors" target="_blank">click to more details</a></strong>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="cascading">Cascading</h3>
                <ul>
                    <li>
                        The css rules of the parent will be applied to its children unles they have thier rules.
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="units">Units</h3>
                <ul>
                    <li>
                        In CSS we need to assigne values for dimensions of elements.
                    </li>
                    <li>
                        There are many units in CSS like inch, cm, px, pt, em, percentage, etc.
                    </li>
                    <li>
                        1 inch = 96 px.
                    </li>
                    <li>
                        1 cm = 37.8 px.
                    </li>
                    <li>
                        1 inch = 72 pt.
                    </li>
                    <li>
                        1 em = value of font-size attribute of the element.
                    </li>
                    <li>
                        The percentage value is relative to the parent or the browser window if the parent is the body element.
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="boxes">Boxes</h3>
                <ul>
                    <li>
                        Any block element represent in a virtual box.
                    </li>
                    <li>
                        The Box has 5 properties to edit it. (width, height, padding, border and margin).
                    </li>
                    <li>
                        There is a floating property. With CSS float, an element can be pushed to the left or right, allowing other elements to wrap around it.
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="colors">Colors</h3>
                <ul>
                    <li>
                        In computer we can represent any color by mixing three basic colors RGB red, green and blue.
                    </li>
                    <li>
                        The value of each color is rang from 0 to 255. 255 most brightness of the color.
                    </li>
                    <li>
                        There is three ways to write RGB values in CSS: 
                    </li>
                        &emsp;1. rgb(255,20,130)&emsp;2. #ff1482 (in hex)&emsp;3. rgb(100%,8%,51%)
                    </li>
                    <li>
                        You can find the value of any color in web page with developer tool in the web browser. 
                    </li>
                    <li>
                        By clicking with shift on the color value you can see diffrent representations of the color.
                    </li>
                    <li>
                        You can use  picker color tools like that <a href="https://www.w3schools.com/colors/colors_picker.asp">tool</a>.
                    </li>
                    <li>
                        You can use hsl to represent a color in CSS.
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="fonts">Fonts</h3>
                <ul>
                    <li>
                        There are many properties for font in CSS.
                    </li>
                    <li>
                        <h4>font-family</h4>
                        <ul>
                            <li>
                                There are generic families like serif, sans-serif, cursive, fantasy and monospace.
                            </li>
                            <li>
                                There are specific families like Helvetica, "Times New Roman", Courier, Palatino and Impact.
                            </li>
                            <li>
                                You should use font stack like <em>font-family: Constantia, Georgia, serif;</em> by starting with specific families then in the end write thier generic family seperated with "," so if the browser don't support specific families then it will display the generic families.
                            </li>
                            <li>
                                You can import fonts from google <a href="https://developers.google.com/fonts/docs/getting_started" target="_blank">click for more detailes</a> and <a href="https://fonts.google.com/" target="_blank"> for fonts list</a>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>font-size:</h4>
                        <ul>
                            <li>
                                To specify the size of text with different units.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>font-weight:</h4>
                        <ul>
                            <li>
                                To specify if the text is bold or not <em>font-weight: bold;</em>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>font-style:</h4>
                        <ul>
                            <li>
                                To specify if the text is italic or not <em>font-style: italic;</em>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>text-decoration:</h4>
                        <ul>
                            <li>
                                To specify if the text is underlined or not <em>text-decoration: underline;</em>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>font property:</h4>
                        <ul>
                            <li>
                                You can max font properties in on property lik <em>font: italic small-caps bold 44px/50px Georgia, sans-serif;</em>
                            </li>
                            <li>
                                The font-family and font-size are Mandatory and other properties are optional.
                            </li>
                            <li>
                                The order of properties is font-style font-variant font-weight font-size/line-height font-family|caption|icon|menu|message-box|small-caption|status-bar|initial|inherit;
                            </li>
                            <li>
                                For more details <a href="https://css-tricks.com/almanac/properties/f/font/" target="_blank">click here</a> or
                                <a href="https://www.w3schools.com/cssref/pr_font_font.asp" target="_blank">click here</a>.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>Note</h4>
                        <ul>
                            <li>
                                font-weight:bold; equal to &lt;strong> element in style and font-style:italic; equal to &lt;em> element.
                            </li>
                            <li>
                                The difference is that the html elements has another porpous to mark the text inside them as important text.
                            </li>
                            <li>
                                Important text is used by search engines or other tools. 
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="display">Display Property</h3>
                <ul>
                    <li>
                        There are many values for this property like:
                    </li>
                    <li>
                        <h4>block</h4>
                        <ul>
                            <li>
                                To display an element (inline at most) as a block element (like &lt;ul>). It starts on a new line, and takes up the whole width.
                            </li>
                            <li>
                                display:block; is not allowed to have other block elements inside it.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>inline</h4>
                        <ul>
                            <li>
                                To display an element as an inline element (like &lt;span>). Any height and width properties will have no effect.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>none</h4>
                        <ul>
                            <li>
                                The element is completely removed.
                            </li>
                        </ul>
                    </li>
                    <li>
                        <h4>flex</h4>
                        <ul>
                            <li>
                                To display an element as a block-level flex container.
                            </li>
                            <li>
                                There are many properties for flex when you use flex value for display property.
                            </li>
                            <li>
                                <strong>flex-direction property</strong>: specifies the direction of the flexible items.
                            </li>
                             <li>
                                <strong>flex-wrap property</strong>: specifies whether the flexible items should wrap or not. It is used to make the items in the flexbox to be moved to fit in the box size.
                             </li>
                             <li>
                                <strong>For more details</strong>
                                <a href="https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout/Basic_Concepts_of_Flexbox" target="_blank">click here</a> or 
                                <a href="https://www.w3schools.com/cssref/css3_pr_flex-wrap.asp" target="_blank">click here</a>.
                             </li>
                        </ul>
                    </li>
                    <li>
                        <h4>For more details</h4>
                        <ul>
                            <li>
                                Go to this <a href="https://www.w3schools.com/cssref/pr_class_display.asp" target="_blank">link</a>.
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="position">position property</h3>
                <ul>
                    <li>
                        Go to this <a href="https://www.w3schools.com/cssref/pr_class_position.asp" target="_blank">link</a>
                    </li>
                </ul>
            </div>
            <div class="section-box">
                <h3 id="more-css">More CSS</h3>
                <ul>
                    <li>
                        There are many properties in CSS. For more details you can go to that
                        <a href="https://developer.mozilla.org/en-US/docs/Web/CSS/Reference" target="_blank">CSS reference</a> , 
                        <a href="https://www.w3schools.com/cssref/pr_class_position.asp" target="_blank">W3 CSS properties</a> ,
                        <a href="https://www.w3schools.com/css/default.asp" target="_blank">W3 CSS tutorial</a> or search in google.
                    </li>
                </ul>
            </div>
        </div>
    </body>
</html>
'''


def CheckURI(uri, timeout=5):
    '''Check whether this URI is reachable, i.e. does it return a 200 OK?

    This function returns True if a GET request to uri returns a 200 OK, and
    False if that GET request returns any other response, or doesn't return
    (i.e. times out).
    '''
    # 1. Write this function.  Delete the following line.
    #raise NotImplementedError("Step 1 isn't written yet.")
    try:
        isValid = requests.get(uri).status_code == 200
        return isValid
    except:
        return False


class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # A GET request will either be for / (the root path) or for /some-name.
        # Strip off the / and we have either empty string or a name.
        name = unquote(self.path[1:])

        if name == 'http/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # List the known associations in the form.
            known = "\n".join("{} : {}".format(key, memory[key])
                              for key in sorted(memory.keys()))
            self.wfile.write(form2.encode())
        elif name:
            if name in memory:
                # 2. Send a 303 redirect to the long URI in memory[name].
                #    Delete the following line.
                #raise NotImplementedError("Step 2 isn't written yet.")
                self.send_response(303)
                self.send_header('Location', memory[name])
                self.end_headers()
            else:
                # We don't know that name! Send a 404 error.
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("I don't know '{}'.".format(name).encode())
        else:
            # Root path. Send the form.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # List the known associations in the form.
            known = "\n".join("{} : {}".format(key, memory[key])
                              for key in sorted(memory.keys()))
            self.wfile.write(form.format(known).encode())

    def do_POST(self):
        # Decode the form data.
        length = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)

        # Check that the user submitted the form fields.
        if "longuri" not in params or "shortname" not in params:
            # 3. Serve a 400 error with a useful message.
            #    Delete the following line.
            #raise NotImplementedError("Step 3 isn't written yet!")
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('there is missing field'.encode())
            return

        longuri = params["longuri"][0]
        shortname = params["shortname"][0]

        if CheckURI(longuri):
            # This URI is good!  Remember it under the specified name.
            memory[shortname] = longuri

            # 4. Serve a redirect to the root page (the form).
            #    Delete the following line.
            #raise NotImplementedError("Step 4 isn't written yet!")
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        else:
            # Didn't successfully fetch the long URI.

            # 5. Send a 404 error with a useful message.
            #    Delete the following line.
            #raise NotImplementedError("Step 5 isn't written yet!")
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("wrong uri".encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))   # Use PORT if it's there.
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, Shortener)
    httpd.serve_forever()
