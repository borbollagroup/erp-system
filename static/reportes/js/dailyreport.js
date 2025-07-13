<script>
function getCookie(n){let v=null;document.cookie.split(';').forEach(c=>{const[p,b]=c.trim().split('=');if(p===n)v=decodeURIComponent(b)});return v}

(function(){
  const form=document.getElementById('report-form');
  const tableIds=['manpower','equipment','activities'];

  // Add/remove rows same as before...

  // Photo handling
  const photos=[];
  const dropZone=document.getElementById('drop-zone');
  const browseBtn=document.getElementById('browse-btn');
  const fileInput=document.getElementById('photo-input');
  const preview=document.getElementById('photo-preview');

  async function compress(file){
    return new Promise(res=>{
      const img=new Image(); const canvas=document.createElement('canvas'); const ctx=canvas.getContext('2d');
      img.onload=()=>{
        let w=img.width,h=img.height,max=1024;
        if(w>h&&w>max){h=h*max/w;w=max;}else if(h>max){w=w*max/h;h=max;}
        canvas.width=w;canvas.height=h;ctx.drawImage(img,0,0,w,h);
        canvas.toBlob(b=>res(new File([b],file.name,{type:'image/jpeg'})),'image/jpeg',0.7);
      };
      img.src=URL.createObjectURL(file);
    });
  }

  function renderPhoto(file){
    const wrapper=document.createElement('div');wrapper.className='position-relative m-1';
    wrapper.style.width='100px';wrapper.style.height='100px';
    const img=document.createElement('img');img.src=URL.createObjectURL(file);
    img.style.width='100%';img.style.height='100%';img.style.objectFit='cover';
    const btn=document.createElement('button');btn.type='button';btn.innerHTML='×';
    btn.className='btn btn-sm btn-danger position-absolute';btn.style.top='2px';btn.style.right='2px';
    btn.onclick=()=>{photos.splice(photos.indexOf(file),1);wrapper.remove();};
    wrapper.append(img,btn);preview.append(wrapper);
  }

  dropZone.addEventListener('dragover',e=>{e.preventDefault();dropZone.classList.add('bg-light');});
  dropZone.addEventListener('dragleave',()=>dropZone.classList.remove('bg-light'));
  dropZone.addEventListener('drop',e=>{e.preventDefault();dropZone.classList.remove('bg-light');
    Array.from(e.dataTransfer.files).forEach(async f=>{const c=await compress(f);photos.push(c);renderPhoto(c);});
  });
  browseBtn.addEventListener('click',()=>fileInput.click());
  fileInput.addEventListener('change',()=>{
    Array.from(fileInput.files).forEach(async f=>{const c=await compress(f);photos.push(c);renderPhoto(c);});
  });

  form.addEventListener('submit',async e=>{
    e.preventDefault();
    if(!form.checkValidity()){form.classList.add('was-validated');return;}
    const data={ project:document.getElementById('id_project').value };
    tableIds.forEach(pref=>{
      data[pref]=[];
      document.querySelectorAll('#'+pref+'-table tbody tr').forEach(tr=>{
        const vals=[...tr.querySelectorAll('input')].map(i=>i.value.trim());
        if(vals.some(v=>v))data[pref].push(vals);
      });
    });
    document.getElementById('id_payload').value=JSON.stringify(data);
    const formData=new FormData(form);
    photos.forEach((f,i)=>formData.append('photos',f,f.name));

    const resp=await fetch(location.href,{method:'POST',credentials:'same-origin',headers:{'X-CSRFToken':getCookie('csrftoken')},body:formData});
    alert(resp.ok?'Report saved!':'Error: '+await resp.text());
  });
})();
</script>