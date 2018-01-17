var wsHost="ws://"+location.host;
function messageClient(userName,messageListener){

    var chat=new Object();
    var onMessageListener=messageListener;
    chat.userName=userName;
    chat.url = wsHost.replace("6001","8012")+"/websocket";
    chat.connect=function(){

        this.websocket = new WebSocket(this.url+"?userName="+this.userName);
        this.websocket.onopen=function(event){

            var eventStr=JSON.stringify(event);
            console.log("on open event: "+eventStr);
        };
        this.websocket.onmessage=function(event){

            var msg = event.data;
            // ignore
            if(msg.indexOf("Welcome")>=0){
                console.log(msg);
                return ;
            }
            //console.log(event.data);
            var msg = JSON.parse(msg);
            // callback
            if(onMessageListener != undefined){
                onMessageListener(msg);
                return ;
            }
        };
        this.websocket.onclose=function(event){
            if(event.code==4741  || ""!=event.reason){
                var logoutMsg = {
                    type:"type_logout",
                    from:"server",
                    to:"client",
                    content: event.reason
                }; 
                onMessageListener(logoutMsg);
            }
            var eventStr=JSON.stringify(event);
            console.log("on  close event: "+eventStr);
        };

        this.websocket.onerror=function(event){

            var eventStr=JSON.stringify(event);

            console.log("on  error event: "+eventStr);


        };
        chat.sendText = function(msg){

            console.log("send msg: "+msg);
            this.websocket.send(msg);

        };
    };
    chat.disconnect=function(){

        this.websocket.close();
    };
    return chat;
}
