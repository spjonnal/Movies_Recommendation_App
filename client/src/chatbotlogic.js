import React, {useState} from 'react';
import './App.css'
function Chatbotlogic(){
    const [query, setUserQuery] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    
    const [llmresponse,setLLMResponse] = useState([
        {from:"mowickie",text:"Hi, how can I help you today?"}
    ]);
    const toggleChat = ()=>setIsOpen(!isOpen);
    const handleLLmInteraction = async () => {
    // Append user query locally
        setLLMResponse(prev => [
            ...prev.slice(-200),
            { from: "user", text: query }
        ]);

    // Prepare conversation context for the backend
        const context = [...llmresponse.slice(-200), { from: "user", text: query }];

        try {
            const response_from_llm = await fetch("http://localhost:4001/api/ask_llm", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ conversation: context })
            });

            const data = await response_from_llm.json();

            setLLMResponse(prev => [
                ...prev.slice(-200),
                { from: "mowickie", text: data.answer }
            ]);
        } catch (err) {
            setLLMResponse(prev => [
                ...prev.slice(-200),
                { from: "mowickie", text: err.toString() }
            ]);
        }

        setUserQuery("");
    };


    return(
        <div>
            <div>
                <button id = "chatbot_button" onClick = {toggleChat}>🧠</button> 
                {
                    isOpen &&(
                        <>
                        <p id = "chatbot_container">
                    
                            {
                                llmresponse.map((msg,ind)=>(
                                    <div  key = {ind} className = {msg.from === "mowickie"? "llm-msg" :"user-msg"}>
                                        
                                        <p id = "chatbot_reply">{msg.text}</p>
                                    </div>
                                ))
                            }
                        </p>
                        <input id = "chatbot_input" placeholder = "enter your text here" value = {query} onChange = {(e)=>setUserQuery(e.target.value)} onKeyDown = {(e)=>e==="Enter" && handleLLmInteraction()}></input>
                        <button id = "submit_button" onClick = {handleLLmInteraction} >Generate response</button>
                        </>
                    )
                }
                
            

            
                
            </div>


        </div>
    )
}


export default Chatbotlogic;