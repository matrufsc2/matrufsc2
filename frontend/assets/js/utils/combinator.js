define("utils/combinator", [], function(){
    "use strict";
    return function getCombinations(arr, n){
        var i,j,k,elem,l = arr.length,childperm,ret=[];
        if(n === 1){
            for(i=0; i < arr.length; i++){
                for(j=0; j < arr[i].length; j++){
                    ret.push([arr[i][j]]);
                }
            }
            return ret;
        }
        else{
            for(i = 0; i < l; i++){
                elem = arr.shift();
                for(j = 0; j < elem.length; j++){
                    childperm = getCombinations(arr.slice(), n-1);
                    for(k = 0; k < childperm.length; k++){
                        ret.push([elem[j]].concat(childperm[k]));
                    }
                }
            }
            return ret;
        }
    };
});