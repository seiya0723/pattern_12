window.addEventListener("load" , function (){

    $("#postcode_search").on("click",function(){ search_postcode(); });

});
function search_postcode(){

    //未入力の場合は処理しない。(出来ればここで郵便番号のフォーマットになっているか正規表現でチェックしたほうが良いだろう)
    if (!$("#postcode").val()){
        return false;
    }

    //http://zipcloud.ibsnet.co.jp/doc/api
    //https://zipcloud.ibsnet.co.jp/api/search?zipcode=7830060 

    $.ajax({
        url: "https://zipcloud.ibsnet.co.jp/api/search?zipcode=" + $("#postcode").val(),
        type: "GET",
    }).done( function(data, status, xhr ) { 
        //このdataは文字列で返ってくるのでまずはJSONに変換させる必要がある。
        json    = JSON.parse(data);

        //都道府県
        console.log(json["results"][0]["address1"])

        //〇〇市
        console.log(json["results"][0]["address2"])

        //〇〇
        console.log(json["results"][0]["address3"])

        $("#prefecture").val(json["results"][0]["address1"]);
        $("#city").val(json["results"][0]["address2"])
        $("#address").val(json["results"][0]["address3"])

    }).fail( function(xhr, status, error) {
        console.log("通信エラー")
    }); 


}

