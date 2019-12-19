function get_wisdom()
{
    ajaxreq = new XMLHttpRequest();
    ajaxreq.onreadystatechange = function()
    {
        if (this.readyState == 4 && this.status == 200)
        {
            document.getElementById("text-block").innerHTML = this.responseText;
        }
    };
    ajaxreq.open("GET", "get_quote", true);
    ajaxreq.send();
}