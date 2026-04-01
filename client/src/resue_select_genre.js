import React from "react";

const SelectGenre = ({name = 'genres', id= "movie_genres", onChange, value})=>{

    const available_genres = [
        {value:'def',label:'--Please Select--'},
         {value:'act', label:'Action'},
         {value:'adv',label:'Adventure'},
         {value:'anim',label:'Animation'},
         {value:'biog',label:'Biography'},
         {value:'com',label:'Comedy'},
         {value:'crm',label:'Crime'},
         {value:'doc',label:'Documentary'},
         {value:'drm',label:'Drama'},
         {value:'fam',label:'Family'},
         {value:'fant',label:'Fantasy'},
         {value : 'flm-noir',label:'Film-Noir'},
         {value:'gm-shw',label:'Game-Show'},
         {value:'hst',label:'History'},
         {value:'hrr',label:'Horror'},
         {value:'msc',label:'Music'},
         {value:'mscal',label:'Musical'},
         {value:'myst',label:'Mystery'},
         {value:'nws',label:'News'},
         {value : 'ralt-tv',label:'Reality-TV'},
         {value : 'rmce',label:'Romance'},
         {value:'sci-fi',label:'Science-Fiction (Sci-Fi)'},
         {value:'srt',label:'Short'},
         {value : 'sprt',label:'Sport'},
         {value: 'tlk-sw',label:'Talk-Show'},
         {value:'thr',label:'Thriller'},
         {value:'war',label:'War'},
         {value:'wst',label:'Western'}
    ];
    const handleDifferentCondition = (e)=>{
        if(typeof onChange === 'function'){
            onChange({ value: e.target.value })
        }
    }
    return(
        
        <select name={name} id = {id} onChange={handleDifferentCondition} value={value}>
        {
            available_genres.map((choice, index)=>(
                <option key={index} value={choice.label}>
                {choice.label}
                </option>
            ))
        }
        </select>
        
    )
}

export default SelectGenre